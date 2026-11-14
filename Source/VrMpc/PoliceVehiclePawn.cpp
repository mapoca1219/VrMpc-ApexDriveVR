// Fill out your copyright notice in the Description page of Project Settings.

#include "PoliceVehiclePawn.h"
#include "Components/PointLightComponent.h"
#include "Components/AudioComponent.h"
#include "Components/SplineComponent.h"
#include "Components/StaticMeshComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "RaceTrackFollowerComponent.h"
#include "RaceTrackSpline.h"
#include "VrVehiclePawn.h"
#include "CarAIAgentComponent.h"
#include "AIController.h"
#include "EngineUtils.h"
#include "UObject/ConstructorHelpers.h"
#include "Kismet/GameplayStatics.h"

APoliceVehiclePawn::APoliceVehiclePawn()
{
	PrimaryActorTick.bCanEverTick = true;
	bIsParkedAmbush = false;

	AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
	AIControllerClass = AAIController::StaticClass();

	// Visual chassis mesh attached to vehicle root
	ChassisMeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ChassisMeshComponent"));
	ChassisMeshComponent->SetupAttachment(RootComponent);
	ChassisMeshComponent->SetCollisionProfileName(TEXT("NoCollision"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> MerkursFinder(TEXT("/Game/Vehicles/Meshes/SM_Merkurs_Chassis.SM_Merkurs_Chassis"));
	if (MerkursFinder.Succeeded())
	{
		ChassisMeshComponent->SetStaticMesh(MerkursFinder.Object);
		ChassisMeshComponent->SetRelativeScale3D(FVector(1.0f, 1.0f, 1.0f));
		ChassisMeshComponent->SetRelativeLocation(FVector(0.0f, 0.0f, 0.0f));
		ChassisMeshComponent->SetRelativeRotation(FRotator(0.0f, 180.0f, 0.0f)); // Aligns vehicle nose forward (+X)
	}

	// Red Siren Light on left roof (roof is at Z ~ 125cm)
	RedSirenLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("RedSirenLight"));
	RedSirenLight->SetupAttachment(RootComponent);
	RedSirenLight->SetRelativeLocation(FVector(0.0f, -25.0f, 132.0f));
	RedSirenLight->SetLightColor(FLinearColor(1.0f, 0.05f, 0.05f));
	RedSirenLight->Intensity = 5000.0f;
	RedSirenLight->AttenuationRadius = 900.0f;
	RedSirenLight->bUseInverseSquaredFalloff = true;
	RedSirenLight->CastShadows = false;

	// Blue Siren Light on right roof
	BlueSirenLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("BlueSirenLight"));
	BlueSirenLight->SetupAttachment(RootComponent);
	BlueSirenLight->SetRelativeLocation(FVector(0.0f, 25.0f, 132.0f));
	BlueSirenLight->SetLightColor(FLinearColor(0.05f, 0.25f, 1.0f));
	BlueSirenLight->Intensity = 5000.0f;
	BlueSirenLight->AttenuationRadius = 900.0f;
	BlueSirenLight->bUseInverseSquaredFalloff = true;
	BlueSirenLight->CastShadows = false;

	// Red Siren Visual Strobe Mesh on roof
	RedSirenMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RedSirenMesh"));
	RedSirenMesh->SetupAttachment(RootComponent);
	RedSirenMesh->SetRelativeLocation(FVector(0.0f, -25.0f, 128.0f));
	RedSirenMesh->SetRelativeScale3D(FVector(0.12f, 0.12f, 0.08f));
	RedSirenMesh->SetCollisionProfileName(TEXT("NoCollision"));

	// Blue Siren Visual Strobe Mesh on roof
	BlueSirenMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BlueSirenMesh"));
	BlueSirenMesh->SetupAttachment(RootComponent);
	BlueSirenMesh->SetRelativeLocation(FVector(0.0f, 25.0f, 128.0f));
	BlueSirenMesh->SetRelativeScale3D(FVector(0.12f, 0.12f, 0.08f));
	BlueSirenMesh->SetCollisionProfileName(TEXT("NoCollision"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> SirenMeshFinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (SirenMeshFinder.Succeeded())
	{
		RedSirenMesh->SetStaticMesh(SirenMeshFinder.Object);
		BlueSirenMesh->SetStaticMesh(SirenMeshFinder.Object);
	}
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> RedMatFinder(TEXT("/Game/Vehicles/Materials/M_Siren_Red.M_Siren_Red"));
	if (RedMatFinder.Succeeded())
	{
		RedSirenMesh->SetMaterial(0, RedMatFinder.Object);
	}
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> BlueMatFinder(TEXT("/Game/Vehicles/Materials/M_Siren_Blue.M_Siren_Blue"));
	if (BlueMatFinder.Succeeded())
	{
		BlueSirenMesh->SetMaterial(0, BlueMatFinder.Object);
	}

	// Spline circuit follower for track patrol
	SplineFollower = CreateDefaultSubobject<URaceTrackFollowerComponent>(TEXT("SplineFollower"));

	// Engine Sound Component
	EngineAudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("EngineAudioComponent"));
	EngineAudioComponent->SetupAttachment(RootComponent);
	EngineAudioComponent->bAutoActivate = true;

	static ConstructorHelpers::FObjectFinder<USoundWave> EngineSoundFinder(TEXT("/Game/Audio/SW_Engine_Loop.SW_Engine_Loop"));
	if (EngineSoundFinder.Succeeded())
	{
		EngineAudioComponent->SetSound(EngineSoundFinder.Object);
		EngineAudioComponent->bAllowSpatialization = true;
	}

	// Police Siren Sound Component
	SirenAudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("SirenAudioComponent"));
	SirenAudioComponent->SetupAttachment(RootComponent);
	SirenAudioComponent->bAutoActivate = false;

	static ConstructorHelpers::FObjectFinder<USoundWave> SirenSoundFinder(TEXT("/Game/Audio/SW_Police_Siren.SW_Police_Siren"));
	if (SirenSoundFinder.Succeeded())
	{
		SirenAudioComponent->SetSound(SirenSoundFinder.Object);
		SirenAudioComponent->bAllowSpatialization = true;
	}

	// Ensure mechanical simulation torque curve in constructor
	if (UChaosWheeledVehicleMovementComponent* ChaosMovement = Cast<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent()))
	{
		ChaosMovement->EngineSetup.TorqueCurve.ExternalCurve = nullptr;
		ChaosMovement->EngineSetup.TorqueCurve.EditorCurveData.Reset();
		ChaosMovement->EngineSetup.TorqueCurve.EditorCurveData.AddKey(0.0f, 400.0f);
		ChaosMovement->EngineSetup.TorqueCurve.EditorCurveData.AddKey(6000.0f, 500.0f);
		ChaosMovement->EngineSetup.MaxRPM = 7000.0f;
	}
}

void APoliceVehiclePawn::BeginPlay()
{
	Super::BeginPlay();

	ChaosMovementComp = Cast<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent());
	if (ChaosMovementComp)
	{
		// Guarantee valid torque curve at runtime so Chaos mechanical simulation is never disabled
		if (ChaosMovementComp->EngineSetup.TorqueCurve.GetRichCurve() == nullptr ||
		    ChaosMovementComp->EngineSetup.TorqueCurve.GetRichCurve()->GetNumKeys() == 0)
		{
			ChaosMovementComp->EngineSetup.TorqueCurve.ExternalCurve = nullptr;
			ChaosMovementComp->EngineSetup.TorqueCurve.EditorCurveData.Reset();
			ChaosMovementComp->EngineSetup.TorqueCurve.EditorCurveData.AddKey(0.0f, 400.0f);
			ChaosMovementComp->EngineSetup.TorqueCurve.EditorCurveData.AddKey(6000.0f, 500.0f);
			ChaosMovementComp->EngineSetup.MaxRPM = 7000.0f;
		}
	}

	FindPlayerPawn();

	// Enforce forward-facing chassis orientation regardless of whether Merkurs or Ioniq mesh is active
	if (ChassisMeshComponent && ChassisMeshComponent->GetStaticMesh())
	{
		const FString MeshName = ChassisMeshComponent->GetStaticMesh()->GetName();
		if (MeshName.Contains(TEXT("Ioniq")))
		{
			// SM_Hyundai_Ioniq5 has length along Y: Yaw -90 aligns its front with vehicle forward (+X)
			ChassisMeshComponent->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
			ChassisMeshComponent->SetRelativeScale3D(FVector(0.0125f, 0.0125f, 0.0125f));
			ChassisMeshComponent->SetRelativeLocation(FVector(0.0f, 0.0f, -76.0f));
		}
		else
		{
			// SM_Merkurs_Chassis has length along X: Yaw 180 aligns vehicle nose forward (+X)
			ChassisMeshComponent->SetRelativeRotation(FRotator(0.0f, 180.0f, 0.0f));
			ChassisMeshComponent->SetRelativeScale3D(FVector(1.0f, 1.0f, 1.0f));
			ChassisMeshComponent->SetRelativeLocation(FVector(0.0f, 0.0f, 0.0f));
		}
	}

	// Auto-detect track spline if not explicitly assigned
	if (!TrackActor.IsValid())
	{
		TrackActor = Cast<ARaceTrackSpline>(UGameplayStatics::GetActorOfClass(GetWorld(), ARaceTrackSpline::StaticClass()));
	}

	if (SplineFollower && !SplineFollower->HasValidSpline() && TrackActor.IsValid())
	{
		USplineComponent* SplineComp = TrackActor->GetSplineComponent();
		if (SplineComp)
		{
			SplineFollower->SetTargetSpline(SplineComp);
		}
	}

	if (EngineAudioComponent && EngineAudioComponent->Sound)
	{
		EngineAudioComponent->SetVolumeMultiplier(0.10f);
		if (!EngineAudioComponent->IsPlaying())
		{
			EngineAudioComponent->Play();
		}
	}
	if (SirenAudioComponent && SirenAudioComponent->Sound)
	{
		SirenAudioComponent->SetVolumeMultiplier(0.12f);
		if (bIsSirenActive && !SirenAudioComponent->IsPlaying())
		{
			SirenAudioComponent->Play();
		}
	}

	// Initialize track progress and lateral offset from initial spawn location
	bIsParkedAmbush = false;
	FallbackPoliceSpeedKmh = 195.0f;
	SetSirenActive(true);

	if (TrackActor.IsValid() && TrackActor->GetSplineComponent())
	{
		USplineComponent* SplineComp = TrackActor->GetSplineComponent();
		const FVector MyLoc = GetActorLocation();
		const float MyKey = SplineComp->FindInputKeyClosestToWorldLocation(MyLoc);
		DistanceAlongTrack = SplineComp->GetDistanceAlongSplineAtSplineInputKey(MyKey);
		const FVector Center = SplineComp->GetLocationAtSplineInputKey(MyKey, ESplineCoordinateSpace::World);
		const FVector RightVec = SplineComp->GetRightVectorAtSplineInputKey(MyKey, ESplineCoordinateSpace::World);
		LateralTrackOffset = FVector::DotProduct(MyLoc - Center, RightVec);
	}
}

void APoliceVehiclePawn::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	UpdateSirenLights(DeltaTime);
	UpdatePursuitAI(DeltaTime);
	CheckProximityAndAlertPlayer();

	if (EngineAudioComponent)
	{
		const float Pitch = FMath::Clamp(0.68f + (GetSpeedKmh() / 200.0f) * 0.42f, 0.65f, 1.15f);
		EngineAudioComponent->SetPitchMultiplier(Pitch);
		EngineAudioComponent->SetVolumeMultiplier(0.10f);
	}
}

void APoliceVehiclePawn::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
}

void APoliceVehiclePawn::SetSirenActive(bool bActive)
{
	bIsSirenActive = bActive;
	if (!bIsSirenActive)
	{
		RedSirenLight->SetVisibility(false);
		BlueSirenLight->SetVisibility(false);
		if (RedSirenMesh) RedSirenMesh->SetVisibility(false);
		if (BlueSirenMesh) BlueSirenMesh->SetVisibility(false);
		if (SirenAudioComponent)
		{
			SirenAudioComponent->Stop();
		}
	}
	else
	{
		if (SirenAudioComponent)
		{
			// Comfortable, non-fatiguing, gentle volume
			SirenAudioComponent->SetVolumeMultiplier(0.12f);
			if (!SirenAudioComponent->IsPlaying())
			{
				SirenAudioComponent->Play();
			}
		}
	}
}

void APoliceVehiclePawn::SetTargetPlayer(AVrVehiclePawn* PlayerPawn)
{
	TargetPlayerPawn = PlayerPawn;
}

float APoliceVehiclePawn::GetSpeedKmh() const
{
	if (GetMesh() && GetMesh()->IsSimulatingPhysics() && ChaosMovementComp)
	{
		const float ChaosSpeed = FMath::Abs(ChaosMovementComp->GetForwardSpeed()) * 0.036f;
		if (ChaosSpeed > 0.5f)
		{
			return ChaosSpeed;
		}
	}
	if (FMath::Abs(FallbackPoliceSpeedKmh) > 0.1f)
	{
		return FMath::Abs(FallbackPoliceSpeedKmh);
	}
	return GetVelocity().Size() * 0.036f;
}

void APoliceVehiclePawn::FindPlayerPawn()
{
	APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(GetWorld(), 0);
	TargetPlayerPawn = Cast<AVrVehiclePawn>(PlayerPawn);
	if (!TargetPlayerPawn.IsValid())
	{
		TargetPlayerPawn = Cast<AVrVehiclePawn>(UGameplayStatics::GetActorOfClass(GetWorld(), AVrVehiclePawn::StaticClass()));
	}
}

void APoliceVehiclePawn::UpdateSirenLights(float DeltaTime)
{
	if (!bIsSirenActive)
	{
		return;
	}

	StrobeTimer += DeltaTime * SirenStrobeRate;

	// High-intensity alternating strobe pattern
	const int32 Phase = FMath::FloorToInt(FMath::Fmod(StrobeTimer * 2.0f, 4.0f));
	const bool bRedOn = (Phase == 0 || Phase == 1);
	const bool bBlueOn = (Phase == 2 || Phase == 3);

	RedSirenLight->SetVisibility(bRedOn);
	BlueSirenLight->SetVisibility(bBlueOn);
	if (RedSirenMesh) RedSirenMesh->SetVisibility(bRedOn);
	if (BlueSirenMesh) BlueSirenMesh->SetVisibility(bBlueOn);
}

void APoliceVehiclePawn::CheckProximityAndAlertPlayer()
{
	TimeSinceLastAlert += GetWorld()->GetDeltaSeconds();

	if (!TargetPlayerPawn.IsValid() || TimeSinceLastAlert < AlertCooldownSeconds)
	{
		return;
	}

	const float DistanceToPlayer = FVector::Dist(GetActorLocation(), TargetPlayerPawn->GetActorLocation());

	// If within 15 meters, trigger Copilot alert on player's AI agent
	if (DistanceToPlayer <= ProximityAlertDistance)
	{
		TimeSinceLastAlert = 0.0f;

		if (UCarAIAgentComponent* AIAgent = TargetPlayerPawn->GetAIAgentComponent())
		{
			AIAgent->SendImmediateEventAlert(
				TEXT("POLICE_ALERT"),
				TEXT("POLICE PATROL ON REAR BUMPER! EVADE!")
			);
		}
	}
}

void APoliceVehiclePawn::UpdatePursuitAI(float DeltaTime)
{
	if (!TrackActor.IsValid())
	{
		TrackActor = Cast<ARaceTrackSpline>(UGameplayStatics::GetActorOfClass(GetWorld(), ARaceTrackSpline::StaticClass()));
	}

	USplineComponent* Spline = TrackActor.IsValid() ? TrackActor->GetSplineComponent() : nullptr;
	const float CurrentSpeed = GetSpeedKmh();
	const FVector PoliceLoc = GetActorLocation();

	// Dynamic Multi-Target Discovery: Prioritize player if within 70m, otherwise target closest racer in conflict
	AVrVehiclePawn* LocalPlayer = Cast<AVrVehiclePawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
	TargetPlayerPawn = nullptr;

	if (LocalPlayer && Spline && Spline->GetSplineLength() > 100.0f)
	{
		const float SplineLen = Spline->GetSplineLength();
		float PDiff = LocalPlayer->GetDistanceAlongTrack() - DistanceAlongTrack;
		if (Spline->IsClosedLoop())
		{
			if (PDiff < -SplineLen * 0.5f) PDiff += SplineLen;
			else if (PDiff > SplineLen * 0.5f) PDiff -= SplineLen;
		}

		if (FMath::Abs(PDiff) < 7000.0f)
		{
			TargetPlayerPawn = LocalPlayer;
		}
	}

	// If player is not within 70m, find the closest active racer (player or rival)
	if (!TargetPlayerPawn.IsValid() && Spline && Spline->GetSplineLength() > 100.0f)
	{
		const float SplineLen = Spline->GetSplineLength();
		float BestAbsDist = 999999.0f;
		for (TActorIterator<AVrVehiclePawn> It(GetWorld()); It; ++It)
		{
			AVrVehiclePawn* Racer = *It;
			if (!Racer) continue;

			float RDiff = Racer->GetDistanceAlongTrack() - DistanceAlongTrack;
			if (Spline->IsClosedLoop())
			{
				if (RDiff < -SplineLen * 0.5f) RDiff += SplineLen;
				else if (RDiff > SplineLen * 0.5f) RDiff -= SplineLen;
			}

			const float AbsD = FMath::Abs(RDiff);
			if (AbsD < 20000.0f && AbsD < BestAbsDist)
			{
				BestAbsDist = AbsD;
				TargetPlayerPawn = Racer;
			}
		}
	}

	if (!TargetPlayerPawn.IsValid())
	{
		TargetPlayerPawn = LocalPlayer;
	}

	// Mute siren if far from local player (>40m) so it never hurts ears
	APawn* LocalPlayerPawn = UGameplayStatics::GetPlayerPawn(GetWorld(), 0);
	if (LocalPlayerPawn && SirenAudioComponent)
	{
		const float DistToPlayer = FVector::Dist(PoliceLoc, LocalPlayerPawn->GetActorLocation());
		if (DistToPlayer > 4000.0f && SirenAudioComponent->IsPlaying())
		{
			SirenAudioComponent->Stop();
		}
		else if (DistToPlayer <= 4000.0f && bIsSirenActive && !SirenAudioComponent->IsPlaying())
		{
			SirenAudioComponent->SetVolumeMultiplier(0.12f);
			SirenAudioComponent->Play();
		}
	}

	float Steer = 0.0f;
	float Throttle = 1.0f;
	float Brake = 0.0f;
	float DesiredSpeed = 200.0f;

	// Parked Ambush State: wait motionless on shoulder with sirens off until any racer approaches
	if (bIsParkedAmbush)
	{
		if (Spline && Spline->GetSplineLength() > 100.0f)
		{
			const float SplineLen = Spline->GetSplineLength();
			for (TActorIterator<AVrVehiclePawn> It(GetWorld()); It; ++It)
			{
				AVrVehiclePawn* Racer = *It;
				if (!Racer) continue;

				float RDiff = Racer->GetDistanceAlongTrack() - DistanceAlongTrack;
				if (Spline->IsClosedLoop())
				{
					if (RDiff < -SplineLen * 0.5f) RDiff += SplineLen;
					else if (RDiff > SplineLen * 0.5f) RDiff -= SplineLen;
				}

				if (RDiff > -6500.0f && RDiff < 2500.0f)
				{
					bIsParkedAmbush = false;
					SetSirenActive(true);
					FallbackPoliceSpeedKmh = 95.0f;
					break;
				}
			}
		}

		if (bIsParkedAmbush)
		{
			SetSirenActive(false);
			FallbackPoliceSpeedKmh = 0.0f;
			if (ChaosMovementComp)
			{
				ChaosMovementComp->SetThrottleInput(0.0f);
				ChaosMovementComp->SetBrakeInput(1.0f);
			}
			return;
		}
	}

	if (TargetPlayerPawn.IsValid() && Spline && Spline->GetSplineLength() > 100.0f)
	{
		const float SplineLen = Spline->GetSplineLength();
		const FVector TargetLoc = TargetPlayerPawn->GetActorLocation();

		const float PoliceKey = Spline->FindInputKeyClosestToWorldLocation(PoliceLoc);
		const float PoliceSplineDist = Spline->GetDistanceAlongSplineAtSplineInputKey(PoliceKey);

		const float TargetKey = Spline->FindInputKeyClosestToWorldLocation(TargetLoc);
		const float TargetSplineDist = Spline->GetDistanceAlongSplineAtSplineInputKey(TargetKey);

		// Signed distance along track circuit:
		// > 0 means Target is ahead of Police (Pursuit)
		// < 0 means Police is ahead of Target (Overtake)
		float DistDiff = TargetSplineDist - PoliceSplineDist;
		if (Spline->IsClosedLoop())
		{
			if (DistDiff < -SplineLen * 0.5f) DistDiff += SplineLen;
			else if (DistDiff > SplineLen * 0.5f) DistDiff -= SplineLen;
		}

		const float Direct3DDistance = FVector::Dist(PoliceLoc, TargetLoc);

		// Target world location: ram target when close, or follow spline ahead
		FVector TargetWorldLoc;
		if (Direct3DDistance < 2000.0f)
		{
			TargetWorldLoc = TargetLoc - (TargetPlayerPawn->GetActorForwardVector() * 40.0f);
		}
		else
		{
			const float LookAhead = FMath::Clamp(FMath::Abs(DistDiff) * 0.7f, 600.0f, 2500.0f);
			float AheadSplineDist = PoliceSplineDist + LookAhead;
			if (Spline->IsClosedLoop())
			{
				AheadSplineDist = FMath::Fmod(AheadSplineDist, SplineLen);
			}
			TargetWorldLoc = Spline->GetLocationAtDistanceAlongSpline(AheadSplineDist, ESplineCoordinateSpace::World);
		}

		// Calculate steering towards target in local space
		FVector LocalTarget = GetActorTransform().InverseTransformPosition(TargetWorldLoc);
		LocalTarget.Z = 0.0f;
		LocalTarget.Normalize();

		Steer = FMath::Clamp(LocalTarget.Y * PursuitSteeringGain, -1.0f, 1.0f);

		// Tactical Pursuit Speed & Throttle:
		const float TargetSpeed = TargetPlayerPawn->GetSpeedKmh();
		DesiredSpeed = 190.0f;

		if (DistDiff > 400.0f)
		{
			// 1. PURSUIT MODE (Target is ahead):
			// Aggressively chase racer, match speed + 25-35 km/h, up to 230 km/h!
			if (DistDiff <= 1800.0f)
			{
				DesiredSpeed = FMath::Clamp(TargetSpeed + 35.0f, 180.0f, 230.0f);
			}
			else
			{
				DesiredSpeed = FMath::Clamp(TargetSpeed + 25.0f, 175.0f, 220.0f);
			}
			Throttle = 1.0f;
			Brake = 0.0f;
		}
		else if (FMath::Abs(DistDiff) <= 400.0f)
		{
			// 2. RAMMING / SIDESWIPE MODE (Alongside target):
			// Match speed and bump hard into the side of the car
			DesiredSpeed = FMath::Max(TargetSpeed + 8.0f, 195.0f);
			Throttle = 1.0f;
			Brake = 0.0f;
		}
		else if (DistDiff < -400.0f && DistDiff >= -3500.0f)
		{
			// 3. ACTIVE LANE BLOCKING (Target is behind police, attempting to pass):
			// Actively match high speed (98% of player) and weave directly in front of their lane!
			DesiredSpeed = FMath::Clamp(TargetSpeed * 0.98f, 185.0f, 225.0f);
			Throttle = 1.0f;
			Brake = 0.0f;
		}
		else
		{
			// 4. Target is far behind (> 35m): Cruise forward at patrol pace
			DesiredSpeed = 180.0f;
			Throttle = 0.90f;
			Brake = 0.0f;
		}
	}
	else if (SplineFollower && SplineFollower->HasValidSpline())
	{
		SplineFollower->ComputeSteeringAndThrottle(CurrentSpeed, Steer, Throttle, Brake);
		Throttle = FMath::Max(Throttle, 0.95f);
	}
	else
	{
		Throttle = 1.0f;
		Brake = 0.0f;
	}

	if (ChaosMovementComp)
	{
		ChaosMovementComp->SetSteeringInput(Steer);
		ChaosMovementComp->SetThrottleInput(Throttle);
		ChaosMovementComp->SetBrakeInput(Brake);
	}

	// Dynamic Kinematic Track-Bound Pursuit (Guarantees rock-solid track alignment, zero tipping/flipping)
	const bool bChaosSimulating = (GetMesh() && GetMesh()->IsSimulatingPhysics());
	if (!bChaosSimulating && Spline && Spline->GetSplineLength() > 100.0f)
	{
		const float SplineLen = Spline->GetSplineLength();

		const float TargetSpeedCap = FMath::Max(DesiredSpeed, 235.0f);
		if (Throttle > 0.01f)
		{
			if (FallbackPoliceSpeedKmh < DesiredSpeed)
			{
				FallbackPoliceSpeedKmh = FMath::Min(FallbackPoliceSpeedKmh + 140.0f * DeltaTime * Throttle, TargetSpeedCap);
			}
			else
			{
				FallbackPoliceSpeedKmh = FMath::FInterpTo(FallbackPoliceSpeedKmh, DesiredSpeed, DeltaTime, 1.8f);
			}
		}
		else if (Brake > 0.01f)
		{
			FallbackPoliceSpeedKmh = FMath::Max(FallbackPoliceSpeedKmh - 120.0f * DeltaTime * Brake, 60.0f);
		}
		else
		{
			FallbackPoliceSpeedKmh = FMath::FInterpTo(FallbackPoliceSpeedKmh, 195.0f, DeltaTime, 1.5f);
		}

		// 1. Advance along track circuit
		const float MoveDeltaDist = (FallbackPoliceSpeedKmh * (100.0f / 3.6f)) * DeltaTime;
		DistanceAlongTrack += MoveDeltaDist;
		DistanceAlongTrack = FMath::Fmod(DistanceAlongTrack, SplineLen);
		if (DistanceAlongTrack < 0.0f)
		{
			DistanceAlongTrack += SplineLen;
		}

		// 2. Lateral offset: Aggressive Combat Lane-Weaving & Road-Blocking
		float DesiredLateral = 0.0f;
		if (TargetPlayerPawn.IsValid())
		{
			float TargetDist = TargetPlayerPawn->GetDistanceAlongTrack() - DistanceAlongTrack;
			if (Spline->IsClosedLoop())
			{
				if (TargetDist < -SplineLen * 0.5f) TargetDist += SplineLen;
				else if (TargetDist > SplineLen * 0.5f) TargetDist -= SplineLen;
			}

			if (TargetDist < -3500.0f)
			{
				DesiredLateral = 0.0f; // Target far behind, stay center
			}
			else if (TargetDist < -300.0f)
			{
				// AGGRESSIVE BLOCKING: Mirror player's lane with high authority so player cannot pass without swerving!
				DesiredLateral = FMath::Clamp(TargetPlayerPawn->GetLateralTrackOffset(), -320.0f, 320.0f);
			}
			else if (FMath::Abs(TargetDist) <= 300.0f)
			{
				// SIDESWIPE / RAMMING: Steer violently into the player!
				const float LatDiff = TargetPlayerPawn->GetLateralTrackOffset() - LateralTrackOffset;
				const float RamSign = (LatDiff >= 0.0f) ? 1.0f : -1.0f;
				DesiredLateral = FMath::Clamp(TargetPlayerPawn->GetLateralTrackOffset() + (RamSign * 60.0f), -340.0f, 340.0f);
			}
			else
			{
				// PURSUIT: Close in directly behind target
				DesiredLateral = FMath::Clamp(TargetPlayerPawn->GetLateralTrackOffset(), -320.0f, 320.0f);
			}
		}
		// High-responsiveness (8.0f) makes police snap directly in front of the player's front bumper!
		LateralTrackOffset = FMath::FInterpTo(LateralTrackOffset, DesiredLateral, DeltaTime, 8.0f);

		// 3. Keep firmly on asphalt surface (0.0cm ride height) with nose pointed forward
		const FVector SplinePos = Spline->GetLocationAtDistanceAlongSpline(DistanceAlongTrack, ESplineCoordinateSpace::World);
		const FVector SplineDir = Spline->GetDirectionAtDistanceAlongSpline(DistanceAlongTrack, ESplineCoordinateSpace::World);
		const FVector SplineRight = Spline->GetRightVectorAtDistanceAlongSpline(DistanceAlongTrack, ESplineCoordinateSpace::World);

		FVector TargetLocation = SplinePos + (SplineRight * LateralTrackOffset);
		FRotator TargetRotation = SplineDir.Rotation();

		if (TrackActor.IsValid())
		{
			TrackActor->ClampVehicleToTrack(TargetLocation, TargetRotation, DeltaTime, 120.0f, 0.0f);
		}

		SetActorLocationAndRotation(TargetLocation, TargetRotation);
	}
	else if (TrackActor.IsValid())
	{
		FVector Loc = GetActorLocation();
		FRotator Rot = GetActorRotation();
		TrackActor->ClampVehicleToTrack(Loc, Rot, DeltaTime, 120.0f, 0.0f);
		SetActorLocationAndRotation(Loc, Rot);
	}
}

void APoliceVehiclePawn::ResetAmbush(float InDistanceAlongTrack, float InLateralOffset)
{
	bIsParkedAmbush = true;
	DistanceAlongTrack = InDistanceAlongTrack;
	LateralTrackOffset = InLateralOffset;
	FallbackPoliceSpeedKmh = 0.0f;
	SetSirenActive(false);

	if (TrackActor.IsValid() && TrackActor->GetSplineComponent())
	{
		USplineComponent* Spline = TrackActor->GetSplineComponent();
		const FVector SplinePos = Spline->GetLocationAtDistanceAlongSpline(DistanceAlongTrack, ESplineCoordinateSpace::World);
		const FVector SplineDir = Spline->GetDirectionAtDistanceAlongSpline(DistanceAlongTrack, ESplineCoordinateSpace::World);
		const FVector SplineRight = Spline->GetRightVectorAtDistanceAlongSpline(DistanceAlongTrack, ESplineCoordinateSpace::World);

		const FVector TargetLocation = SplinePos + (SplineRight * LateralTrackOffset);
		const FRotator TargetRotation = SplineDir.Rotation();
		SetActorLocationAndRotation(TargetLocation, TargetRotation);
	}
}


