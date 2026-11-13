// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/SceneComponent.h"
#include "VirtualSteeringWheelComponent.generated.h"

UENUM(BlueprintType)
enum class EVrHandSide : uint8
{
	Left UMETA(DisplayName = "Left Hand"),
	Right UMETA(DisplayName = "Right Hand")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSteeringAngleChanged, float, NormalizedSteering);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnHandSteeringStateChanged, EVrHandSide, HandSide, bool, bIsGrabbing);

/**
 * Virtual Steering Wheel Component for VR Hands-First vehicle control.
 * Supports Bi-manual and Mono-manual steering with angle calculation and auto-centering.
 */
UCLASS(ClassGroup=(VR), meta=(BlueprintSpawnableComponent))
class VRMPC_API UVirtualSteeringWheelComponent : public USceneComponent
{
	GENERATED_BODY()

public:	
	UVirtualSteeringWheelComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/** Called when a VR hand grips the wheel */
	UFUNCTION(BlueprintCallable, Category = "VR|Steering")
	void StartSteering(EVrHandSide HandSide, USceneComponent* HandComponent);

	/** Called when a VR hand releases the wheel */
	UFUNCTION(BlueprintCallable, Category = "VR|Steering")
	void StopSteering(EVrHandSide HandSide);

	/** Check if a specific hand is currently grabbing the wheel */
	UFUNCTION(BlueprintPure, Category = "VR|Steering")
	bool IsHandGrabbing(EVrHandSide HandSide) const;

	/** Checks if a hand component is within grab distance to the wheel rim */
	UFUNCTION(BlueprintPure, Category = "VR|Steering")
	bool IsInGrabRange(const USceneComponent* HandComponent) const;

	/** Attempts to grab if hand is close enough and grasp strength exceeds threshold */
	UFUNCTION(BlueprintCallable, Category = "VR|Steering")
	bool TryGrab(EVrHandSide HandSide, USceneComponent* HandComponent, float GraspStrength, float Threshold = 0.5f);

	/** Releases hand if grasp strength drops below release threshold */
	UFUNCTION(BlueprintCallable, Category = "VR|Steering")
	void TryRelease(EVrHandSide HandSide, float GraspStrength, float ReleaseThreshold = 0.25f);

	/** Returns current normalized steering value in range [-1.0, 1.0] */
	UFUNCTION(BlueprintPure, Category = "VR|Steering")
	float GetNormalizedSteering() const;

	/** Returns current rotation angle in degrees */
	UFUNCTION(BlueprintPure, Category = "VR|Steering")
	float GetCurrentSteeringAngle() const { return CurrentSteeringAngleDeg; }

	/** Resets the steering wheel to neutral position immediately */
	UFUNCTION(BlueprintCallable, Category = "VR|Steering")
	void ResetToCenter();

	/** Set direct steering angle in degrees (used by gamepad / keyboard input) */
	UFUNCTION(BlueprintCallable, Category = "VR|Steering")
	void SetSteeringAngleDeg(float AngleDeg);

	/** Base tilt pitch angle towards driver in degrees */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Steering")
	float BaseTiltPitch = -24.0f;

	/** Broadcasts normalized steering value [-1.0, 1.0] */
	UPROPERTY(BlueprintAssignable, Category = "VR|Steering")
	FOnSteeringAngleChanged OnSteeringAngleChanged;

	/** Broadcasts when grab state changes */
	UPROPERTY(BlueprintAssignable, Category = "VR|Steering")
	FOnHandSteeringStateChanged OnHandSteeringStateChanged;

	/** Maximum steering angle in each direction in degrees (e.g. 450 = 1.25 turns each way) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Steering")
	float MaxSteeringAngleDeg = 450.0f;

	/** Radius of the steering wheel rim circle in cm (e.g. 16cm = 32cm diameter wheel) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Steering")
	float WheelRimRadius = 16.0f;

	/** Grab interaction tolerance distance from wheel rim in cm */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Steering")
	float GrabRadius = 18.0f;

	/** Speed at which wheel returns to center when released */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Steering")
	float ReturnToCenterSpeed = 12.0f;

	/** Deadzone near zero to prevent jitter in high speed straight lines */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Steering")
	float SteeringDeadZone = 0.02f;

protected:
	virtual void BeginPlay() override;

private:
	bool bIsLeftHandGrabbing = false;
	bool bIsRightHandGrabbing = false;
	bool bIsExternallyControlled = false;

	UPROPERTY()
	TWeakObjectPtr<USceneComponent> LeftHandComp;

	UPROPERTY()
	TWeakObjectPtr<USceneComponent> RightHandComp;

	float CurrentSteeringAngleDeg = 0.0f;
	float InitialHandAngleDeg = 0.0f;
	float InitialWheelAngleDeg = 0.0f;

	/** Calculate raw angle from hands projected onto wheel plane */
	float CalculateRawHandAngleDeg() const;
};
