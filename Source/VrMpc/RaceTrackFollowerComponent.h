// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RaceTrackFollowerComponent.generated.h"

class USplineComponent;

/**
 * Spline Track Follower Component.
 * Enables AI vehicles (rivals and police) to smoothly navigate a closed racing circuit
 * along a 3D Spline, adjusting steering, throttle, and cornering speed dynamically.
 */
UCLASS(ClassGroup=(AI), meta=(BlueprintSpawnableComponent))
class VRMPC_API URaceTrackFollowerComponent : public UActorComponent
{
	GENERATED_BODY()

public:	
	URaceTrackFollowerComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/** Sets or changes the spline curve to follow */
	UFUNCTION(BlueprintCallable, Category = "AI|Spline")
	void SetTargetSpline(USplineComponent* NewSpline);

	/** Computes normalized steering [-1.0, 1.0], throttle [0.0, 1.0], and brake [0.0, 1.0] */
	UFUNCTION(BlueprintCallable, Category = "AI|Spline")
	void ComputeSteeringAndThrottle(float CurrentSpeedKmh, float& OutSteering, float& OutThrottle, float& OutBrake) const;

	/** Returns the predicted future target location on the spline */
	UFUNCTION(BlueprintPure, Category = "AI|Spline")
	FVector GetTargetLocationOnSpline(float CurrentSpeedKmh) const;

	/** Checks if a target spline is validly assigned */
	UFUNCTION(BlueprintPure, Category = "AI|Spline")
	bool HasValidSpline() const;

	/** Spline component of the track to follow */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Spline")
	TObjectPtr<USplineComponent> TargetSplineComponent;

	/** Base lookahead distance in centimeters (e.g. 1200cm = 12m) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Spline")
	float BaseLookAheadDistance = 1200.0f;

	/** Additional lookahead distance scaled by vehicle speed (Base + SpeedKmh * Scale) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Spline")
	float SpeedLookAheadScale = 8.0f;

	/** Target cruising speed in km/h on straight sectors */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Spline")
	float TargetCruisingSpeedKmh = 145.0f;

	/** Minimum speed in sharp corners */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Spline")
	float MinCorneringSpeedKmh = 65.0f;

	/** Steering sensitivity multiplier */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Spline")
	float SteeringGain = 2.2f;

protected:
	virtual void BeginPlay() override;

private:
	mutable float CurrentSplineDistance = 0.0f;
};

