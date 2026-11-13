// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/SplineMeshComponent.h"
#include "RaceTrackSpline.generated.h"

class USplineComponent;
class UStaticMesh;
class UMaterialInterface;

/**
 * Procedural Closed-Circuit Race Track Generator.
 * Generates continuous asphalt road surfaces and protective lateral guardrails
 * along a 3D Spline with full physics and collision support for high-speed VR racing.
 */
UCLASS()
class VRMPC_API ARaceTrackSpline : public AActor
{
	GENERATED_BODY()
	
public:	
	ARaceTrackSpline();

	virtual void OnConstruction(const FTransform& Transform) override;

	/** Accessor for the underlying track Spline */
	UFUNCTION(BlueprintPure, Category = "Track")
	USplineComponent* GetSplineComponent() const { return SplineComponent; }

	/** Clamps a vehicle to the track surface and lateral guardrails, preventing it from ever falling off into the void */
	UFUNCTION(BlueprintCallable, Category = "Track")
	bool ClampVehicleToTrack(FVector& InOutLocation, FRotator& InOutRotation, float DeltaTime, float CarHalfWidth = 110.0f, float GroundOffset = 0.0f) const;

	/** Root Spline component defining the racing circuit geometry */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Track")
	TObjectPtr<USplineComponent> SplineComponent;

	/** Width of the road surface in centimeters (default 1400cm = 14 meters / 3 lanes) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Track|Dimensions")
	float TrackWidth = 1400.0f;

	/** Height of the lateral containment walls / guardrails in cm (70cm = low GT3 barrier allowing full panoramic vision) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Track|Dimensions")
	float WallHeight = 70.0f;

	/** Thickness of the lateral containment walls in cm (35cm sleek Armco barrier) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Track|Dimensions")
	float WallThickness = 35.0f;

	/** Length in cm of each procedural spline mesh slice (default 800cm = 8m for continuous curvature without angular artifacts) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Track|Dimensions")
	float SliceLength = 800.0f;

	/** Whether the race track is a closed looping circuit */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Track|Spline")
	bool bIsClosedLoop = true;

	/** Whether to generate continuous protective walls on track borders */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Track|Guardrails")
	bool bGenerateGuardrails = true;

	/** Mesh asset used for the road surface (defaults to standard 100x100 plane) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Track|Meshes")
	TObjectPtr<UStaticMesh> RoadStaticMesh;

	/** Mesh asset used for lateral guardrails / barriers (defaults to cube) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Track|Meshes")
	TObjectPtr<UStaticMesh> WallStaticMesh;

	/** Optional material override for the road surface (e.g. asphalt) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Track|Materials")
	TObjectPtr<UMaterialInterface> RoadMaterial;

	/** Optional material override for guardrails (e.g. concrete barrier) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Track|Materials")
	TObjectPtr<UMaterialInterface> WallMaterial;

	/** Forward alignment axis for the spline mesh (default X) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Track|Advanced")
	TEnumAsByte<ESplineMeshAxis::Type> ForwardAxis = ESplineMeshAxis::X;

private:
	UPROPERTY()
	TArray<TObjectPtr<USplineMeshComponent>> GeneratedSplineMeshes;

	void ClearGeneratedMeshes();
	void BuildTrackSegment(int32 SegmentIndex, const FVector& StartPos, const FVector& StartTangent, const FVector& EndPos, const FVector& EndTangent);
};

