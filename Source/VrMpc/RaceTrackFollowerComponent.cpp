// Fill out your copyright notice in the Description page of Project Settings.

#include "RaceTrackFollowerComponent.h"
#include "Components/SplineComponent.h"

URaceTrackFollowerComponent::URaceTrackFollowerComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void URaceTrackFollowerComponent::BeginPlay()
{
	Super::BeginPlay();
}

void URaceTrackFollowerComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
}

void URaceTrackFollowerComponent::SetTargetSpline(USplineComponent* NewSpline)
{
	TargetSplineComponent = NewSpline;
}

bool URaceTrackFollowerComponent::HasValidSpline() const
{
	return TargetSplineComponent != nullptr && TargetSplineComponent->GetSplineLength() > 100.0f;
}

FVector URaceTrackFollowerComponent::GetTargetLocationOnSpline(float CurrentSpeedKmh) const
{
	if (!HasValidSpline() || !GetOwner())
	{
		return GetOwner() ? GetOwner()->GetActorLocation() + GetOwner()->GetActorForwardVector() * 1000.0f : FVector::ZeroVector;
	}

	const FVector VehicleLoc = GetOwner()->GetActorLocation();
	const float SplineLength = TargetSplineComponent->GetSplineLength();

	// Find nearest input key and distance along the spline
	const float ClosestInputKey = TargetSplineComponent->FindInputKeyClosestToWorldLocation(VehicleLoc);
	const float NearestDist = TargetSplineComponent->GetDistanceAlongSplineAtSplineInputKey(ClosestInputKey);
	CurrentSplineDistance = NearestDist;

	// Dynamic lookahead based on current vehicle velocity
	const float DynamicLookAhead = BaseLookAheadDistance + (CurrentSpeedKmh * SpeedLookAheadScale);
	float TargetDist = NearestDist + DynamicLookAhead;

	// Handle loop wrap-around or clamp
	if (TargetSplineComponent->IsClosedLoop())
	{
		TargetDist = FMath::Fmod(TargetDist, SplineLength);
		if (TargetDist < 0.0f)
		{
			TargetDist += SplineLength;
		}
	}
	else
	{
		TargetDist = FMath::Clamp(TargetDist, 0.0f, SplineLength);
	}

	return TargetSplineComponent->GetLocationAtDistanceAlongSpline(TargetDist, ESplineCoordinateSpace::World);
}

void URaceTrackFollowerComponent::ComputeSteeringAndThrottle(float CurrentSpeedKmh, float& OutSteering, float& OutThrottle, float& OutBrake) const
{
	OutSteering = 0.0f;
	OutThrottle = 0.0f;
	OutBrake = 0.0f;

	if (!HasValidSpline() || !GetOwner())
	{
		return;
	}

	const FTransform VehicleTransform = GetOwner()->GetActorTransform();
	const FVector TargetWorldLoc = GetTargetLocationOnSpline(CurrentSpeedKmh);

	// Convert vector to target into local vehicle coordinates
	FVector LocalTargetDir = VehicleTransform.InverseTransformVector(TargetWorldLoc - VehicleTransform.GetLocation());
	LocalTargetDir.Z = 0.0f; // Disregard track elevation changes
	LocalTargetDir.Normalize();

	// Local Y represents lateral deviation: positive = right, negative = left
	OutSteering = FMath::Clamp(LocalTargetDir.Y * SteeringGain, -1.0f, 1.0f);

	// Curvature assessment: high lateral target indicates a tight turn ahead
	const float TurnSeverity = FMath::Abs(LocalTargetDir.Y);
	const float DesiredSpeed = FMath::Lerp(TargetCruisingSpeedKmh, MinCorneringSpeedKmh, FMath::Clamp(TurnSeverity * 1.6f, 0.0f, 1.0f));

	if (CurrentSpeedKmh < DesiredSpeed)
	{
		// Accelerate towards desired speed
		const float SpeedDeficit = DesiredSpeed - CurrentSpeedKmh;
		OutThrottle = FMath::Clamp(SpeedDeficit / 25.0f, 0.35f, 1.0f);
		OutBrake = 0.0f;
	}
	else if (CurrentSpeedKmh > DesiredSpeed + 12.0f)
	{
		// Overshooting corner entry speed -> engage brakes
		OutThrottle = 0.0f;
		OutBrake = FMath::Clamp((CurrentSpeedKmh - DesiredSpeed) / 25.0f, 0.3f, 1.0f);
	}
	else
	{
		// Stable coasting speed
		OutThrottle = 0.15f;
		OutBrake = 0.0f;
	}
}

