// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "WheeledVehiclePawn.h"
#include "VirtualSteeringWheelComponent.h"
#include "CarAIAgentComponent.h"
#include "VrVehiclePawn.generated.h"

class UCameraComponent;
class UMotionControllerComponent;
class USkeletalMeshComponent;
class UStaticMeshComponent;
class UWidgetComponent;
class UAudioComponent;
class UChaosWheeledVehicleMovementComponent;
class URaceTrackFollowerComponent;
class UTextRenderComponent;

/**
 * VR Vehicle Pawn integrating Chaos Vehicles with Hands-First VR Steering Wheel,
 * Motion Controller tracking, in-cockpit 3D Dashboard, and Tactical AI Copilot.
 */
UCLASS()
class VRMPC_API AVrVehiclePawn : public AWheeledVehiclePawn
{
	GENERATED_BODY()

public:
	AVrVehiclePawn();

	virtual void Tick(float DeltaTime) override;
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	/** Direct throttle control [0.0, 1.0] */
	UFUNCTION(BlueprintCallable, Category = "VR|Vehicle")
	void SetThrottle(float Value);

	/** Direct brake control [0.0, 1.0] */
	UFUNCTION(BlueprintCallable, Category = "VR|Vehicle")
	void SetBrake(float Value);

	/** Handbrake toggle */
	UFUNCTION(BlueprintCallable, Category = "VR|Vehicle")
	void SetHandbrake(bool bActive);

	/** Nitro boost activation */
	UFUNCTION(BlueprintCallable, Category = "VR|Vehicle")
	void ActivateNitro(bool bActive);

	/** Hands-First Grasp input handler for Left Hand */
	UFUNCTION(BlueprintCallable, Category = "VR|HandsInput")
	void HandleLeftGrasp(float GraspStrength);

	/** Hands-First Grasp input handler for Right Hand */
	UFUNCTION(BlueprintCallable, Category = "VR|HandsInput")
	void HandleRightGrasp(float GraspStrength);

	/** Hands-First Index Curl (Pinch/Trigger) for Brake */
	UFUNCTION(BlueprintCallable, Category = "VR|HandsInput")
	void HandleLeftIndexCurl(float CurlStrength);

	/** Hands-First Index Curl (Pinch/Trigger) for Throttle */
	UFUNCTION(BlueprintCallable, Category = "VR|HandsInput")
	void HandleRightIndexCurl(float CurlStrength);

	/** Forward speed in km/h */
	UFUNCTION(BlueprintPure, Category = "VR|Vehicle")
	float GetSpeedKmh() const;

	/** Restart race after being Busted or finishing */
	UFUNCTION(BlueprintCallable, Category = "VR|Game")
	void RestartRace();

	/** Busted timer in seconds when trapped by police */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Police")
	float BustedTimer = 0.0f;

	/** Total seconds trapped required to get Busted (default 20s) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Police")
	float BustedTimeLimit = 20.0f;

	/** Whether the player has been Busted / Arrested by the police */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Police")
	bool bIsBusted = false;

	/** Race Countdown timer in seconds (3, 2, 1, GO!) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Race")
	float RaceCountdownTimer = 3.99f;

	/** Whether the race is currently active (countdown has completed) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Race")
	bool bIsRaceActive = false;

	/** Lateral bounce velocity from wall collision in cm/s */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Physics")
	float LateralBounceVelocity = 0.0f;

	/** Active Camera View Mode: 0 = Chase Camera (Arcade/Desktop), 1 = Cockpit View, 2 = Hood/Bumper View */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Camera")
	int32 ActiveCameraMode = 0;

	/** Cycle camera mode between Chase, Cockpit and Hood */
	UFUNCTION(BlueprintCallable, Category = "VR|Camera")
	void CycleCameraMode();

	/** Third-person chase camera boom for desktop gameplay */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Camera")
	TObjectPtr<class USpringArmComponent> ChaseCameraBoom;

	/** Third-person chase camera for desktop / non-VR players */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Camera")
	TObjectPtr<class UCameraComponent> ChaseCamera;

	/** Hood / Bumper camera for pure forward perspective */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Camera")
	TObjectPtr<class UCameraComponent> HoodCamera;

	/** Current nitro level in percent [0 - 100] */
	UFUNCTION(BlueprintPure, Category = "VR|Vehicle")
	float GetNitroPercentage() const { return NitroAmount; }

	/** Current lateral displacement from track centerline in cm */
	UFUNCTION(BlueprintPure, Category = "VR|Vehicle")
	float GetLateralTrackOffset() const { return LateralTrackOffset; }

	/** Current distance along track spline in cm */
	UFUNCTION(BlueprintPure, Category = "VR|Vehicle")
	float GetDistanceAlongTrack() const { return DistanceAlongTrack; }

	/** Accessor for Steering Wheel Component */
	UFUNCTION(BlueprintPure, Category = "VR|Vehicle")
	UVirtualSteeringWheelComponent* GetSteeringWheelComponent() const { return SteeringWheelComponent; }

	/** Accessor for AI Spline Follower */
	UFUNCTION(BlueprintPure, Category = "VR|AI")
	URaceTrackFollowerComponent* GetSplineFollower() const { return SplineFollower; }

	/** When true, this vehicle acts as an autonomous AI rival competing in the race */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|AI")
	bool bIsAiRacer = false;

	/** Target cruising speed in km/h for AI rival */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|AI")
	float AiTargetSpeedKmh = 160.0f;

	/** Spline follower component for AI rival navigation */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|AI")
	TObjectPtr<URaceTrackFollowerComponent> SplineFollower;

	/** Accessor for AI Agent Component */
	UFUNCTION(BlueprintPure, Category = "VR|AI")
	UCarAIAgentComponent* GetAIAgentComponent() const { return AIAgentComponent; }

	/** Accessors for Hand Meshes */
	UFUNCTION(BlueprintPure, Category = "VR|Hands")
	USkeletalMeshComponent* GetLeftHandMesh() const { return LeftHandMesh; }

	UFUNCTION(BlueprintPure, Category = "VR|Hands")
	USkeletalMeshComponent* GetRightHandMesh() const { return RightHandMesh; }

	/** Event triggered in Blueprint when the Copilot gives a new tactical order */
	UFUNCTION(BlueprintImplementableEvent, Category = "VR|Copilot")
	void OnCopilotOrderReceived(const FCopilotTacticalOrder& TacticalOrder);

protected:
	virtual void BeginPlay() override;

	/** Visual Static Mesh for the Vehicle Chassis / Exterior Body */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Vehicle")
	TObjectPtr<UStaticMeshComponent> ChassisMeshComponent;

	/** Cockpit HMD Camera for VR driver */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UCameraComponent> VRCamera;

	/** Root scene component for cockpit dashboard, pedals, mirrors */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<USceneComponent> CockpitRoot;

	/** Hands-First Virtual Steering Wheel Pivot */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UVirtualSteeringWheelComponent> SteeringWheelComponent;

	/** Visual Static Mesh for the Steering Wheel */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> SteeringWheelVisualMesh;

	/** Steering Column Support Hub connecting wheel to dashboard */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> SteeringColumnMesh;

	/** High-Tech Cockpit OLED Dashboard Cluster Backplate Housing */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> DashboardBackplateMesh;

	/** Modern EV Wooden / Matte Dashboard Beam Trim (Rivian Dash) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> DashboardWoodTrimMesh;

	/** Warm Amber Ambient LED Light Strip spanning the dashboard */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> AmbientLightStripMesh;

	/** Central Infotainment / Touchscreen Display Anchor (Angled towards driver) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<USceneComponent> CentralDisplayAnchor;

	/** Central 16:9 Widescreen Touchscreen Housing / Bezel */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> CentralTouchscreenMesh;

	/** Central Touchscreen High-Tech OS Title */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UTextRenderComponent> CentralScreenTitle;

	/** Central Touchscreen Drive Modes Selection [SPORT] [OFF-ROAD] [CONSERVE] */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UTextRenderComponent> CentralScreenDriveModes;

	/** Central Touchscreen AI Copilot Tactical Radar & Proximity Status */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UTextRenderComponent> CentralScreenTacticalCopilot;

	/** Central Touchscreen EV Battery / Nitro Boost Bar */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UTextRenderComponent> CentralScreenBatteryNitro;

	/** Central Touchscreen Vehicle Dynamics & Stability Status */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UTextRenderComponent> CentralScreenSubStatus;

	/** Sports Racing Brake Pedal in driver footwell */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> BrakePedalMesh;

	/** Sports Racing Throttle/Accelerator Pedal in driver footwell */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> ThrottlePedalMesh;

	/** Center Console Gear Shift Lever (Caja de cambios) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> GearShiftLeverMesh;

	/** Center Console Gear Shift Knob (Pomo de la palanca) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> GearShiftKnobMesh;

	/** Hands-First Interactive 3D Engine Start/Stop Push Button */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> EngineStartButtonMesh;

	/** Hands-First Interactive 3D Nitro Boost Push Button */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UStaticMeshComponent> NitroButtonMesh;

	/** Dual Rocket Exhaust Nitro Thruster Visual Effects */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Vehicle")
	TObjectPtr<UStaticMeshComponent> LeftNitroFlameMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Vehicle")
	TObjectPtr<UStaticMeshComponent> RightNitroFlameMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Vehicle")
	TObjectPtr<class UPointLightComponent> NitroFlameLight;

	/** Whether the vehicle engine is currently running */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Vehicle")
	bool bIsEngineStarted = true;

	/** Toggles engine state on/off */
	UFUNCTION(BlueprintCallable, Category = "VR|Vehicle")
	void ToggleEngine();

	/** In-Cockpit 3D Digital Speedometer text render */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UTextRenderComponent> SpeedTextRender;

	/** In-Cockpit 3D Race Position text render (e.g. POS: P3 / 7) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UTextRenderComponent> PositionTextRender;

	/** In-Cockpit 3D Current Transmission Gear text render (e.g. GEAR: 3) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UTextRenderComponent> GearTextRender;

	/** In-Cockpit 3D Police Proximity Alert text render */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UTextRenderComponent> PoliceAlertTextRender;

	/** 3D Dashboard Widget for in-cockpit telemetry and copilot messages */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UWidgetComponent> CockpitDisplayWidget;

	/** Radio audio component for copilot voice lines */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UAudioComponent> RadioAudioComponent;

	/** Vehicle Engine Sound component */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Cockpit")
	TObjectPtr<UAudioComponent> EngineAudioComponent;

	/** In-Game Electronic Cyberpunk Soundtrack component (Stereo Surround 2D) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Audio")
	TObjectPtr<UAudioComponent> MusicAudioComponent;

	/** Toggles in-game background music on/off (Key M) */
	UFUNCTION(BlueprintCallable, Category = "VR|Audio")
	void ToggleMusic();

	/** Tactical Copilot AI Agent component */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|AI")
	TObjectPtr<UCarAIAgentComponent> AIAgentComponent;

	/** Left Hand Motion Controller Tracker */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Hands")
	TObjectPtr<UMotionControllerComponent> LeftMotionController;

	/** Right Hand Motion Controller Tracker */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Hands")
	TObjectPtr<UMotionControllerComponent> RightMotionController;

	/** Left Hand Skeletal Mesh */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Hands")
	TObjectPtr<USkeletalMeshComponent> LeftHandMesh;

	/** Right Hand Skeletal Mesh */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Hands")
	TObjectPtr<USkeletalMeshComponent> RightHandMesh;

	/** Nitro depletion rate per second */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Vehicle|Nitro")
	float NitroDepletionRate = 25.0f;

	/** Nitro recharge rate per second when inactive */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Vehicle|Nitro")
	float NitroRechargeRate = 10.0f;

	/** Multiplier added to engine torque / throttle during nitro boost */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Vehicle|Nitro")
	float NitroBoostMultiplier = 1.6f;

	/** Minimum index curl to register throttle/brake */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Vehicle|Input")
	float FingerCurlDeadZone = 0.1f;

	/** Callback when VirtualSteeringWheel computes a new angle */
	UFUNCTION()
	void OnSteeringAngleUpdated(float NormalizedSteering);

	/** Desktop Keyboard and Gamepad Driving Handlers */
	UFUNCTION()
	void OnKeyThrottle(float Val);

	UFUNCTION()
	void OnKeyBrake(float Val);

	UFUNCTION()
	void OnKeySteerLeft(float Val);

	UFUNCTION()
	void OnKeySteerRight(float Val);

	/** Callback when AI Copilot returns tactical instructions */
	UFUNCTION()
	void HandleTacticalAdvice(const FCopilotTacticalOrder& Order);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Race")
	int32 CurrentRacePosition = 4;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Race")
	int32 CurrentLap = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VR|Race")
	int32 TotalLaps = 5;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Race")
	bool bRaceFinished = false;

	float PreviousDistanceAlongTrack = 1200.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Vehicle")
	int32 CurrentGear = 1;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Vehicle")
	int32 PreviousGear = 1;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Vehicle")
	float GearShiftAnimProgress = 1.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Vehicle")
	float DistanceAlongTrack = 1200.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VR|Vehicle")
	float LateralTrackOffset = -160.0f;

private:
	UPROPERTY()
	TObjectPtr<UChaosWheeledVehicleMovementComponent> ChaosMovementComp;

	UPROPERTY()
	TWeakObjectPtr<class ARaceTrackSpline> TrackActor;

	bool bIsNitroActive = false;
	float NitroAmount = 100.0f;
	float CurrentRawThrottle = 0.0f;
	float CurrentSteeringInput = 0.0f;
	float AxisSteerInput = 0.0f;
	float FallbackSpeedKmh = 0.0f;
	float TelemetryUpdateTimer = 0.0f;

	void UpdateCockpitTelemetry(float DeltaTime);
	void UpdateRacePosition();
	void TriggerHapticFeedback(float Intensity, float Duration, bool bLeftHand, bool bRightHand);
};
