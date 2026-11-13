// Fill out your copyright notice in the Description page of Project Settings.

#include "RaceTrackSpline.h"
#include "Components/SplineComponent.h"
#include "Components/SplineMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

ARaceTrackSpline::ARaceTrackSpline()
{
	PrimaryActorTick.bCanEverTick = false;

	SplineComponent = CreateDefaultSubobject<USplineComponent>(TEXT("SplineComponent"));
	RootComponent = SplineComponent;
	SplineComponent->SetClosedLoop(bIsClosedLoop, false);

	// Load built-in engine basic shapes so track renders out of the box
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeFinder(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (CubeFinder.Succeeded())
	{
		RoadStaticMesh = CubeFinder.Object; // Solid 3D Cube for full asphalt slab thickness
		WallStaticMesh = CubeFinder.Object;
	}

	static ConstructorHelpers::FObjectFinder<UMaterialInterface> RoadMatFinder(TEXT("/Game/LevelPrototyping/Materials/M_City_Highway_Asphalt.M_City_Highway_Asphalt"));
	if (RoadMatFinder.Succeeded())
	{
		RoadMaterial = RoadMatFinder.Object;
	}

	static ConstructorHelpers::FObjectFinder<UMaterialInterface> WallMatFinder(TEXT("/Game/LevelPrototyping/Materials/MI_PrototypeGrid_TopDark.MI_PrototypeGrid_TopDark"));
	if (WallMatFinder.Succeeded())
	{
		WallMaterial = WallMatFinder.Object;
	}
}

void ARaceTrackSpline::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);

	if (!SplineComponent)
	{
		return;
	}

	// Guarantee realistic dark highway asphalt and sleek dark GT3 guardrails
	if (!RoadMaterial || RoadMaterial->GetName().Contains(TEXT("Default")))
	{
		UMaterialInterface* FoundAsphalt = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/LevelPrototyping/Materials/M_City_Highway_Asphalt.M_City_Highway_Asphalt"));
		if (FoundAsphalt)
		{
			RoadMaterial = FoundAsphalt;
		}
	}
	if (!WallMaterial || WallMaterial->GetName().Contains(TEXT("NeonCyan")) || WallMaterial->GetName().Contains(TEXT("Metal_-_Chrome")) || WallMaterial->GetName().Contains(TEXT("Default")))
	{
		UMaterialInterface* FoundWall = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/LevelPrototyping/Materials/MI_PrototypeGrid_TopDark.MI_PrototypeGrid_TopDark"));
		if (FoundWall)
		{
			WallMaterial = FoundWall;
		}
	}

	SplineComponent->SetClosedLoop(bIsClosedLoop, true);

	ClearGeneratedMeshes();

	const float SplineLength = SplineComponent->GetSplineLength();
	if (SplineLength < 100.0f)
	{
		return;
	}

	// Subdivide the circuit into short, continuous slices (default 800cm = 8 meters per slice)
	// This ensures even simple meshes curve seamlessly with zero angular artifacts or gaps!
	const float EffectiveSliceLen = FMath::Clamp(SliceLength, 300.0f, 2000.0f);
	const int32 NumSlices = FMath::Max(1, FMath::RoundToInt(SplineLength / EffectiveSliceLen));
	const float StepDist = SplineLength / static_cast<float>(NumSlices);

	for (int32 i = 0; i < NumSlices; ++i)
	{
		const float StartDist = i * StepDist;
		const float EndDist = (i + 1) * StepDist;

		const FVector StartPos = SplineComponent->GetLocationAtDistanceAlongSpline(StartDist, ESplineCoordinateSpace::Local);
		const FVector StartDir = SplineComponent->GetDirectionAtDistanceAlongSpline(StartDist, ESplineCoordinateSpace::Local);
		const FVector StartTangent = StartDir * StepDist;

		// If closed loop and last slice, connect seamlessly back to distance 0
		const FVector EndPos = (bIsClosedLoop && i == NumSlices - 1)
			? SplineComponent->GetLocationAtDistanceAlongSpline(0.0f, ESplineCoordinateSpace::Local)
			: SplineComponent->GetLocationAtDistanceAlongSpline(EndDist, ESplineCoordinateSpace::Local);

		const FVector EndDir = (bIsClosedLoop && i == NumSlices - 1)
			? SplineComponent->GetDirectionAtDistanceAlongSpline(0.0f, ESplineCoordinateSpace::Local)
			: SplineComponent->GetDirectionAtDistanceAlongSpline(EndDist, ESplineCoordinateSpace::Local);
		const FVector EndTangent = EndDir * StepDist;

		BuildTrackSegment(i, StartPos, StartTangent, EndPos, EndTangent);
	}
}

void ARaceTrackSpline::ClearGeneratedMeshes()
{
	for (USplineMeshComponent* MeshComp : GeneratedSplineMeshes)
	{
		if (MeshComp && MeshComp->IsValidLowLevel())
		{
			MeshComp->DestroyComponent();
		}
	}
	GeneratedSplineMeshes.Empty();

	// Catch and clear any stray components registered previously
	TArray<USplineMeshComponent*> ExistingSplineMeshes;
	GetComponents<USplineMeshComponent>(ExistingSplineMeshes);
	for (USplineMeshComponent* StrayComp : ExistingSplineMeshes)
	{
		if (StrayComp && StrayComp->IsValidLowLevel())
		{
			StrayComp->DestroyComponent();
		}
	}
}

void ARaceTrackSpline::BuildTrackSegment(int32 SegmentIndex, const FVector& StartPos, const FVector& StartTangent, const FVector& EndPos, const FVector& EndTangent)
{
	// 1. Generate Road Surface (Solid 3D Asphalt slab with 20cm thickness)
	if (RoadStaticMesh)
	{
		USplineMeshComponent* RoadComp = NewObject<USplineMeshComponent>(this);
		RoadComp->SetMobility(EComponentMobility::Movable);
		RoadComp->SetupAttachment(SplineComponent);
		RoadComp->SetStaticMesh(RoadStaticMesh);
		RoadComp->SetForwardAxis(ForwardAxis, false);
		RoadComp->SetStartAndEnd(StartPos, StartTangent, EndPos, EndTangent, false);

		// WidthScale = 1400 / 100 = 14x. HeightScale = 0.20f (20cm thick solid asphalt slab)
		const float RoadWidthScale = TrackWidth / 100.0f;
		const float RoadThicknessScale = 0.20f;
		RoadComp->SetStartScale(FVector2D(RoadWidthScale, RoadThicknessScale), false);
		RoadComp->SetEndScale(FVector2D(RoadWidthScale, RoadThicknessScale), false);

		// Offset down by 10cm so the top surface of the road sits flush with Spline.Z = 0
		RoadComp->SetStartOffset(FVector2D(0.0f, -10.0f), false);
		RoadComp->SetEndOffset(FVector2D(0.0f, -10.0f), false);

		RoadComp->SetCollisionProfileName(TEXT("BlockAll"));
		RoadComp->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
		RoadComp->SetGenerateOverlapEvents(true);

		if (RoadMaterial)
		{
			RoadComp->SetMaterial(0, RoadMaterial);
		}

		RoadComp->RegisterComponent();
		GeneratedSplineMeshes.Add(RoadComp);
	}

	// 2. Generate Lateral Guardrails / Protective Barriers
	if (bGenerateGuardrails && WallStaticMesh)
	{
		const float WallThicknessScale = WallThickness / 100.0f;
		const float WallHeightScale = WallHeight / 100.0f;
		const float HalfWidth = TrackWidth * 0.5f;
		const float HalfHeight = WallHeight * 0.5f;

		// --- Left Wall ---
		USplineMeshComponent* LeftWall = NewObject<USplineMeshComponent>(this);
		LeftWall->SetMobility(EComponentMobility::Movable);
		LeftWall->SetupAttachment(SplineComponent);
		LeftWall->SetStaticMesh(WallStaticMesh);
		LeftWall->SetForwardAxis(ForwardAxis, false);
		LeftWall->SetStartAndEnd(StartPos, StartTangent, EndPos, EndTangent, false);
		LeftWall->SetStartOffset(FVector2D(-HalfWidth, HalfHeight), false);
		LeftWall->SetEndOffset(FVector2D(-HalfWidth, HalfHeight), false);
		LeftWall->SetStartScale(FVector2D(WallThicknessScale, WallHeightScale), false);
		LeftWall->SetEndScale(FVector2D(WallThicknessScale, WallHeightScale), false);
		LeftWall->SetCollisionProfileName(TEXT("BlockAll"));
		LeftWall->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);

		if (WallMaterial)
		{
			LeftWall->SetMaterial(0, WallMaterial);
		}

		LeftWall->RegisterComponent();
		GeneratedSplineMeshes.Add(LeftWall);

		// --- Right Wall ---
		USplineMeshComponent* RightWall = NewObject<USplineMeshComponent>(this);
		RightWall->SetMobility(EComponentMobility::Movable);
		RightWall->SetupAttachment(SplineComponent);
		RightWall->SetStaticMesh(WallStaticMesh);
		RightWall->SetForwardAxis(ForwardAxis, false);
		RightWall->SetStartAndEnd(StartPos, StartTangent, EndPos, EndTangent, false);
		RightWall->SetStartOffset(FVector2D(HalfWidth, HalfHeight), false);
		RightWall->SetEndOffset(FVector2D(HalfWidth, HalfHeight), false);
		RightWall->SetStartScale(FVector2D(WallThicknessScale, WallHeightScale), false);
		RightWall->SetEndScale(FVector2D(WallThicknessScale, WallHeightScale), false);
		RightWall->SetCollisionProfileName(TEXT("BlockAll"));
		RightWall->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);

		if (WallMaterial)
		{
			RightWall->SetMaterial(0, WallMaterial);
		}

		RightWall->RegisterComponent();
		GeneratedSplineMeshes.Add(RightWall);
	}
}

bool ARaceTrackSpline::ClampVehicleToTrack(FVector& InOutLocation, FRotator& InOutRotation, float DeltaTime, float CarHalfWidth, float GroundOffset) const
{
	if (!SplineComponent || SplineComponent->GetSplineLength() < 100.0f)
	{
		return false;
	}

	const float ClosestKey = SplineComponent->FindInputKeyClosestToWorldLocation(InOutLocation);
	const FVector SplinePos = SplineComponent->GetLocationAtSplineInputKey(ClosestKey, ESplineCoordinateSpace::World);
	const FVector SplineDir = SplineComponent->GetDirectionAtSplineInputKey(ClosestKey, ESplineCoordinateSpace::World);
	const FVector SplineRight = SplineComponent->GetRightVectorAtSplineInputKey(ClosestKey, ESplineCoordinateSpace::World);

	// Vector from track centerline to vehicle
	const FVector OffsetFromSpline = InOutLocation - SplinePos;
	const float LateralDistance = FVector::DotProduct(OffsetFromSpline, SplineRight);

	// Impenetrable barrier margin: 560cm from centerline (safe distance inside the 640cm wall face on 14m road)
	const float MaxLateralAllowed = 560.0f;

	bool bHitWall = false;

	// Inviolable Lateral Clamping: Pushes vehicle smoothly back onto the asphalt
	if (LateralDistance > MaxLateralAllowed)
	{
		bHitWall = true;
		InOutLocation = SplinePos + (SplineRight * MaxLateralAllowed) + ((InOutLocation.Z - SplinePos.Z) * FVector::UpVector);
	}
	else if (LateralDistance < -MaxLateralAllowed)
	{
		bHitWall = true;
		InOutLocation = SplinePos - (SplineRight * MaxLateralAllowed) + ((InOutLocation.Z - SplinePos.Z) * FVector::UpVector);
	}

	// Road Surface Z Alignment (Keep vehicle planted firmly on the asphalt)
	const float DesiredZ = SplinePos.Z + GroundOffset;
	InOutLocation.Z = FMath::FInterpTo(InOutLocation.Z, DesiredZ, DeltaTime, 25.0f);

	// Smoothly conform Pitch to track elevation
	InOutRotation.Pitch = FMath::FInterpTo(InOutRotation.Pitch, SplineDir.Rotation().Pitch, DeltaTime, 15.0f);
	InOutRotation.Roll  = FMath::FInterpTo(InOutRotation.Roll, 0.0f, DeltaTime, 15.0f);

	return bHitWall;
}


