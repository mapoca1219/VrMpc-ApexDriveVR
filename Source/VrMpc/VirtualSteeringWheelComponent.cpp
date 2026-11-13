// Fill out your copyright notice in the Description page of Project Settings.

#include "VirtualSteeringWheelComponent.h"

UVirtualSteeringWheelComponent::UVirtualSteeringWheelComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PrePhysics;
}

void UVirtualSteeringWheelComponent::BeginPlay()
{
	Super::BeginPlay();
	CurrentSteeringAngleDeg = 0.0f;
}

bool UVirtualSteeringWheelComponent::IsInGrabRange(const USceneComponent* HandComponent) const
{
	if (!HandComponent)
	{
		return false;
	}

	// Transform hand location into wheel local space
	// In wheel space: X is column axis (forward), Y is right, Z is up
	const FVector LocalPos = GetComponentTransform().InverseTransformPosition(HandComponent->GetComponentLocation());

	// Distance from center to hand in the wheel disc plane (YZ)
	const float RadialDist = FMath::Sqrt(LocalPos.Y * LocalPos.Y + LocalPos.Z * LocalPos.Z);

	// Distance to the circular rim ring
	const float DistToRimTorus = FMath::Sqrt(FMath::Square(RadialDist - WheelRimRadius) + FMath::Square(LocalPos.X));

	return DistToRimTorus <= GrabRadius;
}

bool UVirtualSteeringWheelComponent::TryGrab(EVrHandSide HandSide, USceneComponent* HandComponent, float GraspStrength, float Threshold)
{
	if (!HandComponent)
	{
		return false;
	}

	// Already grabbing this side
	if (IsHandGrabbing(HandSide))
	{
		return true;
	}

	// Hand must meet grasp threshold and be close to rim
	if (GraspStrength >= Threshold && IsInGrabRange(HandComponent))
	{
		StartSteering(HandSide, HandComponent);
		return true;
	}

	return false;
}

void UVirtualSteeringWheelComponent::TryRelease(EVrHandSide HandSide, float GraspStrength, float ReleaseThreshold)
{
	if (IsHandGrabbing(HandSide) && GraspStrength < ReleaseThreshold)
	{
		StopSteering(HandSide);
	}
}

void UVirtualSteeringWheelComponent::StartSteering(EVrHandSide HandSide, USceneComponent* HandComponent)
{
	if (!HandComponent)
	{
		return;
	}

	bIsExternallyControlled = false;

	if (HandSide == EVrHandSide::Left)
	{
		bIsLeftHandGrabbing = true;
		LeftHandComp = HandComponent;
	}
	else
	{
		bIsRightHandGrabbing = true;
		RightHandComp = HandComponent;
	}

	// Capture initial baseline so wheel does not snap when grabbed
	InitialHandAngleDeg = CalculateRawHandAngleDeg();
	InitialWheelAngleDeg = CurrentSteeringAngleDeg;

	OnHandSteeringStateChanged.Broadcast(HandSide, true);
}

void UVirtualSteeringWheelComponent::StopSteering(EVrHandSide HandSide)
{
	if (HandSide == EVrHandSide::Left)
	{
		bIsLeftHandGrabbing = false;
		LeftHandComp.Reset();
	}
	else
	{
		bIsRightHandGrabbing = false;
		RightHandComp.Reset();
	}

	OnHandSteeringStateChanged.Broadcast(HandSide, false);

	// If one hand remains, re-anchor baseline to the remaining hand to avoid jumps
	if (bIsLeftHandGrabbing || bIsRightHandGrabbing)
	{
		InitialHandAngleDeg = CalculateRawHandAngleDeg();
		InitialWheelAngleDeg = CurrentSteeringAngleDeg;
	}
}

bool UVirtualSteeringWheelComponent::IsHandGrabbing(EVrHandSide HandSide) const
{
	return (HandSide == EVrHandSide::Left) ? bIsLeftHandGrabbing : bIsRightHandGrabbing;
}

float UVirtualSteeringWheelComponent::GetNormalizedSteering() const
{
	if (FMath::IsNearlyZero(MaxSteeringAngleDeg))
	{
		return 0.0f;
	}

	float Normalized = CurrentSteeringAngleDeg / MaxSteeringAngleDeg;
	if (FMath::Abs(Normalized) < SteeringDeadZone)
	{
		return 0.0f;
	}

	return FMath::Clamp(Normalized, -1.0f, 1.0f);
}

void UVirtualSteeringWheelComponent::ResetToCenter()
{
	CurrentSteeringAngleDeg = 0.0f;
	SetRelativeRotation(FRotator(BaseTiltPitch, 0.0f, 0.0f));
}

void UVirtualSteeringWheelComponent::SetSteeringAngleDeg(float AngleDeg)
{
	bIsExternallyControlled = true;
	CurrentSteeringAngleDeg = FMath::Clamp(AngleDeg, -MaxSteeringAngleDeg, MaxSteeringAngleDeg);
	SetRelativeRotation(FRotator(BaseTiltPitch, 0.0f, CurrentSteeringAngleDeg));
	OnSteeringAngleChanged.Broadcast(GetNormalizedSteering());
}

float UVirtualSteeringWheelComponent::CalculateRawHandAngleDeg() const
{
	const FTransform CompTransform = GetComponentTransform();

	// Bi-manual calculation: angle of vector connecting Left and Right hand
	if (bIsLeftHandGrabbing && bIsRightHandGrabbing && LeftHandComp.IsValid() && RightHandComp.IsValid())
	{
		FVector LocalLeft = CompTransform.InverseTransformPosition(LeftHandComp->GetComponentLocation());
		FVector LocalRight = CompTransform.InverseTransformPosition(RightHandComp->GetComponentLocation());

		// In wheel local space: X is forward (steering column), Y is right, Z is up
		FVector HandDelta = LocalRight - LocalLeft;
		float AngleRad = FMath::Atan2(HandDelta.Z, HandDelta.Y);
		return FMath::RadiansToDegrees(AngleRad);
	}
	// Single right hand calculation
	else if (bIsRightHandGrabbing && RightHandComp.IsValid())
	{
		FVector LocalPos = CompTransform.InverseTransformPosition(RightHandComp->GetComponentLocation());
		float AngleRad = FMath::Atan2(LocalPos.Z, LocalPos.Y);
		return FMath::RadiansToDegrees(AngleRad) - 90.0f;
	}
	// Single left hand calculation
	else if (bIsLeftHandGrabbing && LeftHandComp.IsValid())
	{
		FVector LocalPos = CompTransform.InverseTransformPosition(LeftHandComp->GetComponentLocation());
		float AngleRad = FMath::Atan2(LocalPos.Z, LocalPos.Y);
		return FMath::RadiansToDegrees(AngleRad) + 90.0f;
	}

	return 0.0f;
}

void UVirtualSteeringWheelComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (bIsLeftHandGrabbing || bIsRightHandGrabbing)
	{
		bIsExternallyControlled = false;
		float CurrentHandAngle = CalculateRawHandAngleDeg();
		float DeltaAngle = FMath::FindDeltaAngleDegrees(InitialHandAngleDeg, CurrentHandAngle);
		float TargetAngle = InitialWheelAngleDeg + DeltaAngle;

		CurrentSteeringAngleDeg = FMath::Clamp(TargetAngle, -MaxSteeringAngleDeg, MaxSteeringAngleDeg);
		SetRelativeRotation(FRotator(BaseTiltPitch, 0.0f, CurrentSteeringAngleDeg));
		OnSteeringAngleChanged.Broadcast(GetNormalizedSteering());
	}
	else if (bIsExternallyControlled)
	{
		// Rotation driven by keyboard/gamepad/AI input, preserve steering angle
		SetRelativeRotation(FRotator(BaseTiltPitch, 0.0f, CurrentSteeringAngleDeg));
	}
	else
	{
		// Smooth auto-centering spring
		CurrentSteeringAngleDeg = FMath::FInterpTo(CurrentSteeringAngleDeg, 0.0f, DeltaTime, ReturnToCenterSpeed);
		SetRelativeRotation(FRotator(BaseTiltPitch, 0.0f, CurrentSteeringAngleDeg));
		OnSteeringAngleChanged.Broadcast(GetNormalizedSteering());
	}
}
