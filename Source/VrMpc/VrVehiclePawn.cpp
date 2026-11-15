// Fill out your copyright notice in the Description page of Project Settings.

#include "VrVehiclePawn.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "MotionControllerComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/WidgetComponent.h"
#include "Components/AudioComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/PointLightComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "CarAIAgentComponent.h"
#include "RaceTrackSpline.h"
#include "RaceTrackFollowerComponent.h"
#include "Components/SplineComponent.h"
#include "PoliceVehiclePawn.h"
#include "EngineUtils.h"
#include "UObject/ConstructorHelpers.h"
#include "Kismet/GameplayStatics.h"
#include "HeadMountedDisplayFunctionLibrary.h"

AVrVehiclePawn::AVrVehiclePawn()
{
	PrimaryActorTick.bCanEverTick = true;

	// Player possession defaults for VR cockpit
	AutoPossessPlayer = EAutoReceiveInput::Player0;
	AutoPossessAI = EAutoPossessAI::Disabled;

	// Visual chassis mesh attached to vehicle root
	// Visual chassis mesh attached to vehicle root (Rotated 180 so headlights point +X forward down the track)
	ChassisMeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ChassisMeshComponent"));
	ChassisMeshComponent->SetupAttachment(RootComponent);
	ChassisMeshComponent->SetCollisionProfileName(TEXT("NoCollision"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> MerkursFinder(TEXT("/Game/Vehicles/Meshes/SM_Merkurs_Chassis.SM_Merkurs_Chassis"));
	if (MerkursFinder.Succeeded())
	{
		ChassisMeshComponent->SetStaticMesh(MerkursFinder.Object);
		// Plant wheels firmly on the asphalt surface (no hovering)
		ChassisMeshComponent->SetRelativeLocation(FVector(0.0f, 0.0f, -14.0f));
		ChassisMeshComponent->SetRelativeRotation(FRotator(0.0f, 180.0f, 0.0f));
	}

	// Cockpit anchor aligned at natural driver eye level with clear expansive view of road and rivals
	CockpitRoot = CreateDefaultSubobject<USceneComponent>(TEXT("CockpitRoot"));
	CockpitRoot->SetupAttachment(GetMesh());
	CockpitRoot->SetRelativeLocation(FVector(52.0f, -36.0f, 128.0f));
	CockpitRoot->SetRelativeRotation(FRotator(-5.0f, 0.0f, 0.0f));

	// HMD Camera anchored in driver cockpit looking forward down the track (+X)
	VRCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("VRCamera"));
	VRCamera->SetupAttachment(CockpitRoot);
	VRCamera->SetRelativeLocation(FVector::ZeroVector);
	VRCamera->bUsePawnControlRotation = false; // VR head tracking controls camera directly

	// Third-Person Chase Camera for Desktop Gameplay (spectacular arcade view for players without VR headset)
	ChaseCameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("ChaseCameraBoom"));
	ChaseCameraBoom->SetupAttachment(RootComponent);
	ChaseCameraBoom->SetRelativeLocation(FVector(0.0f, 0.0f, 155.0f));
	ChaseCameraBoom->TargetArmLength = 520.0f;
	ChaseCameraBoom->SetRelativeRotation(FRotator(-11.0f, 0.0f, 0.0f));
	ChaseCameraBoom->bEnableCameraLag = true;
	ChaseCameraBoom->CameraLagSpeed = 16.0f;
	ChaseCameraBoom->bDoCollisionTest = false;

	ChaseCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("ChaseCamera"));
	ChaseCamera->SetupAttachment(ChaseCameraBoom);
	ChaseCamera->SetRelativeLocation(FVector::ZeroVector);
	ChaseCamera->SetRelativeRotation(FRotator(0.0f, 0.0f, 0.0f));

	// Front Hood Camera (clean unobstructed forward perspective without dashboard clipping)
	HoodCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("HoodCamera"));
	HoodCamera->SetupAttachment(RootComponent);
	HoodCamera->SetRelativeLocation(FVector(230.0f, 0.0f, 70.0f));
	HoodCamera->SetRelativeRotation(FRotator(-4.0f, 0.0f, 0.0f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeFinder(TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderFinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereFinder(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WheelFinder(TEXT("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered.SM_Steering_Wheel_Centered"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> WheelMatFinder(TEXT("/Game/Vehicles/Materials/M_SteeringWheel_Alcantara.M_SteeringWheel_Alcantara"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> SirenRedFinder(TEXT("/Game/Vehicles/Materials/M_Siren_Red.M_Siren_Red"));

	// High-Tech Cockpit OLED Dashboard Cluster Backplate Housing (Elevated well above steering wheel and hood cowl)
	DashboardBackplateMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DashboardBackplateMesh"));
	DashboardBackplateMesh->SetupAttachment(CockpitRoot);
	DashboardBackplateMesh->SetRelativeLocation(FVector(37.0f, 0.0f, 8.5f));
	DashboardBackplateMesh->SetRelativeRotation(FRotator(-16.0f, 0.0f, 0.0f));
	DashboardBackplateMesh->SetRelativeScale3D(FVector(0.015f, 0.44f, 0.15f));
	DashboardBackplateMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (CubeFinder.Succeeded())
	{
		DashboardBackplateMesh->SetStaticMesh(CubeFinder.Object);
	}
	if (WheelMatFinder.Succeeded())
	{
		DashboardBackplateMesh->SetMaterial(0, WheelMatFinder.Object);
	}

	// Modern EV Dashboard Beam Trim
	DashboardWoodTrimMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DashboardWoodTrimMesh"));
	DashboardWoodTrimMesh->SetupAttachment(CockpitRoot);
	DashboardWoodTrimMesh->SetRelativeLocation(FVector(40.0f, 18.0f, 7.0f));
	DashboardWoodTrimMesh->SetRelativeRotation(FRotator(-14.0f, 0.0f, 0.0f));
	DashboardWoodTrimMesh->SetRelativeScale3D(FVector(0.06f, 1.10f, 0.035f));
	DashboardWoodTrimMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (CubeFinder.Succeeded())
	{
		DashboardWoodTrimMesh->SetStaticMesh(CubeFinder.Object);
	}
	if (WheelMatFinder.Succeeded())
	{
		DashboardWoodTrimMesh->SetMaterial(0, WheelMatFinder.Object);
	}

	// Warm Amber Ambient LED Light Strip spanning the dashboard
	AmbientLightStripMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AmbientLightStripMesh"));
	AmbientLightStripMesh->SetupAttachment(CockpitRoot);
	AmbientLightStripMesh->SetRelativeLocation(FVector(39.5f, 18.0f, 5.2f));
	AmbientLightStripMesh->SetRelativeRotation(FRotator(-14.0f, 0.0f, 0.0f));
	AmbientLightStripMesh->SetRelativeScale3D(FVector(0.012f, 1.10f, 0.012f));
	AmbientLightStripMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (CubeFinder.Succeeded())
	{
		AmbientLightStripMesh->SetStaticMesh(CubeFinder.Object);
	}
	if (SirenRedFinder.Succeeded())
	{
		AmbientLightStripMesh->SetMaterial(0, SirenRedFinder.Object);
	}

	// Central Infotainment / Touchscreen Display Anchor (Embedded low in center console, non-intrusive)
	CentralDisplayAnchor = CreateDefaultSubobject<USceneComponent>(TEXT("CentralDisplayAnchor"));
	CentralDisplayAnchor->SetupAttachment(CockpitRoot);
	CentralDisplayAnchor->SetRelativeLocation(FVector(34.0f, 24.0f, -44.0f));
	CentralDisplayAnchor->SetRelativeRotation(FRotator(-22.0f, -24.0f, 0.0f));

	// Central Touchscreen Housing / Bezel
	CentralTouchscreenMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CentralTouchscreenMesh"));
	CentralTouchscreenMesh->SetupAttachment(CentralDisplayAnchor);
	CentralTouchscreenMesh->SetRelativeLocation(FVector(0.8f, 0.0f, 0.0f));
	CentralTouchscreenMesh->SetRelativeRotation(FRotator(0.0f, 0.0f, 0.0f));
	CentralTouchscreenMesh->SetRelativeScale3D(FVector(0.010f, 0.22f, 0.13f));
	CentralTouchscreenMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (CubeFinder.Succeeded())
	{
		CentralTouchscreenMesh->SetStaticMesh(CubeFinder.Object);
	}
	if (WheelMatFinder.Succeeded())
	{
		CentralTouchscreenMesh->SetMaterial(0, WheelMatFinder.Object);
	}

	// Central Touchscreen OS Title
	CentralScreenTitle = CreateDefaultSubobject<UTextRenderComponent>(TEXT("CentralScreenTitle"));
	CentralScreenTitle->SetupAttachment(CentralDisplayAnchor);
	CentralScreenTitle->SetRelativeLocation(FVector(-0.5f, 0.0f, 7.0f));
	CentralScreenTitle->SetRelativeRotation(FRotator(0.0f, 180.0f, 0.0f));
	CentralScreenTitle->SetText(FText::FromString(TEXT("// GT-VR HYPERCAR | TELEMETRY //")));
	CentralScreenTitle->SetTextRenderColor(FColor(255, 170, 20));
	CentralScreenTitle->SetWorldSize(1.0f);
	CentralScreenTitle->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);

	// Central Touchscreen Drive Modes Selection
	CentralScreenDriveModes = CreateDefaultSubobject<UTextRenderComponent>(TEXT("CentralScreenDriveModes"));
	CentralScreenDriveModes->SetupAttachment(CentralDisplayAnchor);
	CentralScreenDriveModes->SetRelativeLocation(FVector(-0.5f, 0.0f, 3.8f));
	CentralScreenDriveModes->SetRelativeRotation(FRotator(0.0f, 180.0f, 0.0f));
	CentralScreenDriveModes->SetText(FText::FromString(TEXT("[ SPORT* ]   [ ALL-PURPOSE ]   [ NITRO: READY ]")));
	CentralScreenDriveModes->SetTextRenderColor(FColor(0, 255, 180));
	CentralScreenDriveModes->SetWorldSize(1.0f);
	CentralScreenDriveModes->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);

	// Central Touchscreen AI Copilot Tactical Radar & Proximity Status
	CentralScreenTacticalCopilot = CreateDefaultSubobject<UTextRenderComponent>(TEXT("CentralScreenTacticalCopilot"));
	CentralScreenTacticalCopilot->SetupAttachment(CentralDisplayAnchor);
	CentralScreenTacticalCopilot->SetRelativeLocation(FVector(-0.5f, 0.0f, 0.5f));
	CentralScreenTacticalCopilot->SetRelativeRotation(FRotator(0.0f, 180.0f, 0.0f));
	CentralScreenTacticalCopilot->SetText(FText::FromString(TEXT("AI COPILOT: ONLINE (GEMINI 2.5) | RADAR: CLEAR")));
	CentralScreenTacticalCopilot->SetTextRenderColor(FColor(180, 235, 255));
	CentralScreenTacticalCopilot->SetWorldSize(1.25f);
	CentralScreenTacticalCopilot->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);

	// Central Touchscreen EV Battery / Nitro Boost Bar
	CentralScreenBatteryNitro = CreateDefaultSubobject<UTextRenderComponent>(TEXT("CentralScreenBatteryNitro"));
	CentralScreenBatteryNitro->SetupAttachment(CentralDisplayAnchor);
	CentralScreenBatteryNitro->SetRelativeLocation(FVector(-0.5f, 0.0f, -3.5f));
	CentralScreenBatteryNitro->SetRelativeRotation(FRotator(0.0f, 180.0f, 0.0f));
	CentralScreenBatteryNitro->SetText(FText::FromString(TEXT("EV BATTERY: 100%  ||  NITRO BOOST: [ 100% READY ]")));
	CentralScreenBatteryNitro->SetTextRenderColor(FColor(255, 215, 0));
	CentralScreenBatteryNitro->SetWorldSize(1.25f);
	CentralScreenBatteryNitro->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);

	// Central Touchscreen Vehicle Dynamics & Stability Status
	CentralScreenSubStatus = CreateDefaultSubobject<UTextRenderComponent>(TEXT("CentralScreenSubStatus"));
	CentralScreenSubStatus->SetupAttachment(CentralDisplayAnchor);
	CentralScreenSubStatus->SetRelativeLocation(FVector(-0.5f, 0.0f, -7.5f));
	CentralScreenSubStatus->SetRelativeRotation(FRotator(0.0f, 180.0f, 0.0f));
	CentralScreenSubStatus->SetText(FText::FromString(TEXT("REGEN: HIGH  |  RIDE HEIGHT: SPORT -38mm  |  STABILITY: ACTIVE")));
	CentralScreenSubStatus->SetTextRenderColor(FColor(140, 180, 205));
	CentralScreenSubStatus->SetWorldSize(1.05f);
	CentralScreenSubStatus->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);

	// Sports Racing Brake Pedal in driver footwell
	BrakePedalMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BrakePedalMesh"));
	BrakePedalMesh->SetupAttachment(CockpitRoot);
	BrakePedalMesh->SetRelativeLocation(FVector(65.0f, -8.0f, -54.0f));
	BrakePedalMesh->SetRelativeRotation(FRotator(-28.0f, 0.0f, 0.0f));
	BrakePedalMesh->SetRelativeScale3D(FVector(0.025f, 0.08f, 0.14f));
	BrakePedalMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (CubeFinder.Succeeded())
	{
		BrakePedalMesh->SetStaticMesh(CubeFinder.Object);
	}
	if (WheelMatFinder.Succeeded())
	{
		BrakePedalMesh->SetMaterial(0, WheelMatFinder.Object);
	}

	// Sports Racing Throttle/Accelerator Pedal in driver footwell
	ThrottlePedalMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ThrottlePedalMesh"));
	ThrottlePedalMesh->SetupAttachment(CockpitRoot);
	ThrottlePedalMesh->SetRelativeLocation(FVector(65.0f, 6.0f, -56.0f));
	ThrottlePedalMesh->SetRelativeRotation(FRotator(-28.0f, 0.0f, 0.0f));
	ThrottlePedalMesh->SetRelativeScale3D(FVector(0.025f, 0.05f, 0.16f));
	ThrottlePedalMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (CubeFinder.Succeeded())
	{
		ThrottlePedalMesh->SetStaticMesh(CubeFinder.Object);
	}
	if (WheelMatFinder.Succeeded())
	{
		ThrottlePedalMesh->SetMaterial(0, WheelMatFinder.Object);
	}

	// Steering Column Support Hub connecting wheel to dashboard binnacle
	SteeringColumnMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SteeringColumnMesh"));
	SteeringColumnMesh->SetupAttachment(CockpitRoot);
	SteeringColumnMesh->SetRelativeLocation(FVector(44.0f, 0.0f, -18.0f));
	SteeringColumnMesh->SetRelativeRotation(FRotator(-18.0f, 0.0f, 0.0f));
	SteeringColumnMesh->SetRelativeScale3D(FVector(0.05f, 0.05f, 0.12f));
	SteeringColumnMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (CylinderFinder.Succeeded())
	{
		SteeringColumnMesh->SetStaticMesh(CylinderFinder.Object);
	}
	if (WheelMatFinder.Succeeded())
	{
		SteeringColumnMesh->SetMaterial(0, WheelMatFinder.Object);
	}

	// Virtual Steering Wheel attached in front of driver seat (lowered ergonomically to lower margin of view)
	SteeringWheelComponent = CreateDefaultSubobject<UVirtualSteeringWheelComponent>(TEXT("SteeringWheelComponent"));
	SteeringWheelComponent->SetupAttachment(CockpitRoot);
	SteeringWheelComponent->SetRelativeLocation(FVector(30.0f, 0.0f, -24.0f));
	SteeringWheelComponent->BaseTiltPitch = -18.0f;
	SteeringWheelComponent->SetRelativeRotation(FRotator(-18.0f, 0.0f, 0.0f)); // Tilted towards driver

	// 3D Visual Mesh for Steering Wheel (rotates automatically with SteeringWheelComponent)
	SteeringWheelVisualMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SteeringWheelVisualMesh"));
	SteeringWheelVisualMesh->SetupAttachment(SteeringWheelComponent);
	SteeringWheelVisualMesh->SetRelativeLocation(FVector::ZeroVector);
	SteeringWheelVisualMesh->SetRelativeRotation(FRotator(0.0f, 0.0f, 0.0f));
	// Circular sports racing wheel (~32cm diameter, ergonomically framed in lower third of FOV)
	SteeringWheelVisualMesh->SetRelativeScale3D(FVector(85.0f, 85.0f, 85.0f));
	SteeringWheelVisualMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (WheelFinder.Succeeded())
	{
		SteeringWheelVisualMesh->SetStaticMesh(WheelFinder.Object);
	}
	if (WheelMatFinder.Succeeded())
	{
		SteeringWheelVisualMesh->SetMaterial(0, WheelMatFinder.Object);
	}

	// Center Console Gear Shift Lever (Caja de cambios)
	GearShiftLeverMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("GearShiftLeverMesh"));
	GearShiftLeverMesh->SetupAttachment(CockpitRoot);
	GearShiftLeverMesh->SetRelativeLocation(FVector(25.0f, 24.0f, -25.0f));
	GearShiftLeverMesh->SetRelativeRotation(FRotator(-12.0f, 0.0f, 0.0f));
	GearShiftLeverMesh->SetRelativeScale3D(FVector(0.025f, 0.025f, 0.14f));
	GearShiftLeverMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (CylinderFinder.Succeeded())
	{
		GearShiftLeverMesh->SetStaticMesh(CylinderFinder.Object);
	}
	if (WheelMatFinder.Succeeded())
	{
		GearShiftLeverMesh->SetMaterial(0, WheelMatFinder.Object);
	}

	GearShiftKnobMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("GearShiftKnobMesh"));
	GearShiftKnobMesh->SetupAttachment(GearShiftLeverMesh);
	GearShiftKnobMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 48.0f));
	GearShiftKnobMesh->SetRelativeScale3D(FVector(2.4f, 2.4f, 0.45f));
	GearShiftKnobMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (SphereFinder.Succeeded())
	{
		GearShiftKnobMesh->SetStaticMesh(SphereFinder.Object);
	}
	if (WheelMatFinder.Succeeded())
	{
		GearShiftKnobMesh->SetMaterial(0, WheelMatFinder.Object);
	}

	// Hands-First Interactive 3D Engine Start/Stop Push Button (Red racing button on dashboard)
	EngineStartButtonMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("EngineStartButtonMesh"));
	EngineStartButtonMesh->SetupAttachment(CockpitRoot);
	EngineStartButtonMesh->SetRelativeLocation(FVector(43.5f, 18.0f, -12.0f));
	EngineStartButtonMesh->SetRelativeRotation(FRotator(-15.0f, 0.0f, 0.0f));
	EngineStartButtonMesh->SetRelativeScale3D(FVector(0.045f, 0.045f, 0.025f));
	EngineStartButtonMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (CylinderFinder.Succeeded())
	{
		EngineStartButtonMesh->SetStaticMesh(CylinderFinder.Object);
	}

	// Hands-First Interactive 3D Nitro Boost Push Button (Cyan button on center console)
	NitroButtonMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NitroButtonMesh"));
	NitroButtonMesh->SetupAttachment(CockpitRoot);
	NitroButtonMesh->SetRelativeLocation(FVector(28.0f, 20.0f, -22.0f));
	NitroButtonMesh->SetRelativeRotation(FRotator(-12.0f, 0.0f, 0.0f));
	NitroButtonMesh->SetRelativeScale3D(FVector(0.045f, 0.045f, 0.03f));
	NitroButtonMesh->SetCollisionProfileName(TEXT("NoCollision"));
	if (CylinderFinder.Succeeded())
	{
		NitroButtonMesh->SetStaticMesh(CylinderFinder.Object);
	}

	// Dual Rocket Exhaust Nitro Thruster Visual Effects (Visible at rear of car)
	static ConstructorHelpers::FObjectFinder<UStaticMesh> ConeFinder(TEXT("/Engine/BasicShapes/Cone.Cone"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> CyanFlameMatFinder(TEXT("/Game/Vehicles/Materials/M_Siren_Blue.M_Siren_Blue"));

	LeftNitroFlameMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LeftNitroFlameMesh"));
	LeftNitroFlameMesh->SetupAttachment(RootComponent);
	LeftNitroFlameMesh->SetRelativeLocation(FVector(-245.0f, -38.0f, 24.0f));
	LeftNitroFlameMesh->SetRelativeRotation(FRotator(-90.0f, 0.0f, 0.0f));
	LeftNitroFlameMesh->SetRelativeScale3D(FVector(0.12f, 0.12f, 0.38f));
	LeftNitroFlameMesh->SetCollisionProfileName(TEXT("NoCollision"));
	LeftNitroFlameMesh->SetVisibility(false);
	if (ConeFinder.Succeeded())
	{
		LeftNitroFlameMesh->SetStaticMesh(ConeFinder.Object);
	}
	else if (CylinderFinder.Succeeded())
	{
		LeftNitroFlameMesh->SetStaticMesh(CylinderFinder.Object);
	}
	if (CyanFlameMatFinder.Succeeded())
	{
		LeftNitroFlameMesh->SetMaterial(0, CyanFlameMatFinder.Object);
	}

	RightNitroFlameMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RightNitroFlameMesh"));
	RightNitroFlameMesh->SetupAttachment(RootComponent);
	RightNitroFlameMesh->SetRelativeLocation(FVector(-245.0f, 38.0f, 24.0f));
	RightNitroFlameMesh->SetRelativeRotation(FRotator(-90.0f, 0.0f, 0.0f));
	RightNitroFlameMesh->SetRelativeScale3D(FVector(0.12f, 0.12f, 0.38f));
	RightNitroFlameMesh->SetCollisionProfileName(TEXT("NoCollision"));
	RightNitroFlameMesh->SetVisibility(false);
	if (ConeFinder.Succeeded())
	{
		RightNitroFlameMesh->SetStaticMesh(ConeFinder.Object);
	}
	else if (CylinderFinder.Succeeded())
	{
		RightNitroFlameMesh->SetStaticMesh(CylinderFinder.Object);
	}
	if (CyanFlameMatFinder.Succeeded())
	{
		RightNitroFlameMesh->SetMaterial(0, CyanFlameMatFinder.Object);
	}

	NitroFlameLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("NitroFlameLight"));
	NitroFlameLight->SetupAttachment(RootComponent);
	NitroFlameLight->SetRelativeLocation(FVector(-245.0f, 0.0f, 25.0f));
	NitroFlameLight->SetLightColor(FLinearColor(0.1f, 0.85f, 1.0f));
	NitroFlameLight->Intensity = 8000.0f;
	NitroFlameLight->AttenuationRadius = 600.0f;
	NitroFlameLight->SetVisibility(false);

	// In-Cockpit 3D Digital Speedometer (Mounted on Dashboard Cluster facing driver, elevated above wheel)
	SpeedTextRender = CreateDefaultSubobject<UTextRenderComponent>(TEXT("SpeedTextRender"));
	SpeedTextRender->SetupAttachment(CockpitRoot);
	SpeedTextRender->SetRelativeLocation(FVector(35.5f, 0.0f, 8.5f));
	SpeedTextRender->SetRelativeRotation(FRotator(-16.0f, 180.0f, 0.0f));
	SpeedTextRender->SetText(FText::FromString(TEXT("0 KM/H")));
	SpeedTextRender->SetTextRenderColor(FColor(0, 245, 255));
	SpeedTextRender->SetWorldSize(3.8f);
	SpeedTextRender->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);

	// In-Cockpit 3D Race Position (POS: P4 / 7) - Top Left of Dashboard
	PositionTextRender = CreateDefaultSubobject<UTextRenderComponent>(TEXT("PositionTextRender"));
	PositionTextRender->SetupAttachment(CockpitRoot);
	PositionTextRender->SetRelativeLocation(FVector(35.5f, -11.0f, 13.0f));
	PositionTextRender->SetRelativeRotation(FRotator(-16.0f, 180.0f, 0.0f));
	PositionTextRender->SetText(FText::FromString(TEXT("POS: P4/7")));
	PositionTextRender->SetTextRenderColor(FColor(255, 215, 0));
	PositionTextRender->SetWorldSize(2.2f);
	PositionTextRender->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);

	// In-Cockpit 3D Current Gear (GEAR: 1) - Top Center of Dashboard
	GearTextRender = CreateDefaultSubobject<UTextRenderComponent>(TEXT("GearTextRender"));
	GearTextRender->SetupAttachment(CockpitRoot);
	GearTextRender->SetRelativeLocation(FVector(35.5f, 11.0f, 13.0f));
	GearTextRender->SetRelativeRotation(FRotator(-16.0f, 180.0f, 0.0f));
	GearTextRender->SetText(FText::FromString(TEXT("GEAR: 1")));
	GearTextRender->SetTextRenderColor(FColor(255, 140, 0));
	GearTextRender->SetWorldSize(2.2f);
	GearTextRender->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);

	// In-Cockpit 3D Police Proximity Warning - Bottom Bar of Dashboard
	PoliceAlertTextRender = CreateDefaultSubobject<UTextRenderComponent>(TEXT("PoliceAlertTextRender"));
	PoliceAlertTextRender->SetupAttachment(CockpitRoot);
	PoliceAlertTextRender->SetRelativeLocation(FVector(35.5f, 0.0f, 4.2f));
	PoliceAlertTextRender->SetRelativeRotation(FRotator(-16.0f, 180.0f, 0.0f));
	PoliceAlertTextRender->SetText(FText::FromString(TEXT("PATROL STATUS: CLEAR")));
	PoliceAlertTextRender->SetTextRenderColor(FColor(0, 255, 128));
	PoliceAlertTextRender->SetWorldSize(1.6f);
	PoliceAlertTextRender->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);

	// 3D Dashboard Widget for in-cockpit HUD & Copilot messages
	CockpitDisplayWidget = CreateDefaultSubobject<UWidgetComponent>(TEXT("CockpitDisplayWidget"));
	CockpitDisplayWidget->SetupAttachment(CockpitRoot);
	CockpitDisplayWidget->SetRelativeLocation(FVector(45.0f, 0.0f, -2.0f));
	CockpitDisplayWidget->SetRelativeRotation(FRotator(-25.0f, 0.0f, 0.0f));
	CockpitDisplayWidget->SetDrawSize(FVector2D(400.0f, 180.0f));
	CockpitDisplayWidget->SetWidgetSpace(EWidgetSpace::World);
	CockpitDisplayWidget->SetCollisionProfileName(TEXT("NoCollision"));

	// Radio speaker audio component for copilot voice lines
	RadioAudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("RadioAudioComponent"));
	RadioAudioComponent->SetupAttachment(CockpitRoot);
	RadioAudioComponent->SetRelativeLocation(FVector(20.0f, 25.0f, 5.0f));
	RadioAudioComponent->bAutoActivate = false;

	static ConstructorHelpers::FObjectFinder<USoundWave> RadioSoundFinder(TEXT("/Game/Audio/SW_Copilot_Radio.SW_Copilot_Radio"));
	if (RadioSoundFinder.Succeeded())
	{
		RadioAudioComponent->SetSound(RadioSoundFinder.Object);
	}

	// Vehicle Engine Sound component
	EngineAudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("EngineAudioComponent"));
	EngineAudioComponent->SetupAttachment(CockpitRoot);
	EngineAudioComponent->bAutoActivate = true;

	static ConstructorHelpers::FObjectFinder<USoundWave> EngineSoundFinder(TEXT("/Game/Audio/SW_Engine_Loop.SW_Engine_Loop"));
	if (EngineSoundFinder.Succeeded())
	{
		EngineAudioComponent->SetSound(EngineSoundFinder.Object);
		EngineAudioComponent->bAllowSpatialization = true;
	}

	// In-Game Cyberpunk Racing Soundtrack (Head-Locked 2D Stereo Surround)
	MusicAudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("MusicAudioComponent"));
	MusicAudioComponent->SetupAttachment(CockpitRoot);
	MusicAudioComponent->bAutoActivate = true;
	MusicAudioComponent->bIsUISound = true;
	MusicAudioComponent->bAllowSpatialization = false; // Pure stereo surrounding the driver
	MusicAudioComponent->SetVolumeMultiplier(0.35f);

	static ConstructorHelpers::FObjectFinder<USoundWave> MusicFinder(TEXT("/Game/Audio/SW_Synthwave_Music.SW_Synthwave_Music"));
	if (MusicFinder.Succeeded())
	{
		MusicAudioComponent->SetSound(MusicFinder.Object);
	}

	// Tactical AI Copilot Agent
	AIAgentComponent = CreateDefaultSubobject<UCarAIAgentComponent>(TEXT("AIAgentComponent"));
	AIAgentComponent->BackendEndpointUrl = TEXT("http://127.0.0.1:8000/api/v1/copilot/tactics");
	AIAgentComponent->TelemetryIntervalSeconds = 2.0f;

	// Left Hand Tracker
	LeftMotionController = CreateDefaultSubobject<UMotionControllerComponent>(TEXT("LeftMotionController"));
	LeftMotionController->SetupAttachment(CockpitRoot);
	LeftMotionController->SetTrackingMotionSource(FName("LeftGrip"));

	LeftHandMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("LeftHandMesh"));
	LeftHandMesh->SetupAttachment(LeftMotionController);
	LeftHandMesh->SetCollisionProfileName(TEXT("NoCollision"));

	// Right Hand Tracker
	RightMotionController = CreateDefaultSubobject<UMotionControllerComponent>(TEXT("RightMotionController"));
	RightMotionController->SetupAttachment(CockpitRoot);
	RightMotionController->SetTrackingMotionSource(FName("RightGrip"));

	RightHandMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("RightHandMesh"));
	RightHandMesh->SetupAttachment(RightMotionController);
	RightHandMesh->SetCollisionProfileName(TEXT("NoCollision"));

	// AI Spline Follower for AI Rivals
	SplineFollower = CreateDefaultSubobject<URaceTrackFollowerComponent>(TEXT("SplineFollower"));

	// Default mechanical simulation torque curve in constructor
	if (UChaosWheeledVehicleMovementComponent* ChaosMovement = Cast<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent()))
	{
		ChaosMovement->EngineSetup.TorqueCurve.ExternalCurve = nullptr;
		ChaosMovement->EngineSetup.TorqueCurve.EditorCurveData.Reset();
		ChaosMovement->EngineSetup.TorqueCurve.EditorCurveData.AddKey(0.0f, 400.0f);
		ChaosMovement->EngineSetup.TorqueCurve.EditorCurveData.AddKey(6000.0f, 500.0f);
		ChaosMovement->EngineSetup.MaxRPM = 7000.0f;
	}
}

void AVrVehiclePawn::BeginPlay()
{
	Super::BeginPlay();

	// Determine if this pawn is an AI rival or player controlled
	APlayerController* MyPC = Cast<APlayerController>(GetController());
	if (GetName().Contains(TEXT("Rival")) || (!MyPC && this != UGameplayStatics::GetPlayerPawn(GetWorld(), 0)))
	{
		bIsAiRacer = true;
	}
	else
	{
		bIsAiRacer = false;
	}

	// Ensure mesh physics simulation is disabled so the rock-solid track-bound spline kinematics drive the vehicle
	if (GetMesh())
	{
		GetMesh()->SetSimulatePhysics(false);
	}

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

	if (SteeringWheelComponent)
	{
		SteeringWheelComponent->OnSteeringAngleChanged.AddDynamic(this, &AVrVehiclePawn::OnSteeringAngleUpdated);
	}

	if (AIAgentComponent)
	{
		AIAgentComponent->OnTacticalAdviceReceived.AddDynamic(this, &AVrVehiclePawn::HandleTacticalAdvice);
	}

	if (EngineAudioComponent && EngineAudioComponent->Sound)
	{
		EngineAudioComponent->SetVolumeMultiplier(bIsAiRacer ? 0.08f : 0.28f);
		if (!EngineAudioComponent->IsPlaying())
		{
			EngineAudioComponent->Play();
		}
	}

	// In-Game Music: Local player only (non-spatialized head-locked stereo)
	if (!bIsAiRacer && MusicAudioComponent && MusicAudioComponent->Sound)
	{
		MusicAudioComponent->SetVolumeMultiplier(0.35f);
		if (!MusicAudioComponent->IsPlaying())
		{
			MusicAudioComponent->Play();
		}
	}
	else if (bIsAiRacer && MusicAudioComponent)
	{
		MusicAudioComponent->Stop();
	}

	if (bIsAiRacer)
	{
		// Disable VR camera, hands, and HUD for autonomous AI rival pawns
		if (VRCamera) VRCamera->SetActive(false);
		if (LeftMotionController) LeftMotionController->SetActive(false);
		if (RightMotionController) RightMotionController->SetActive(false);
		if (LeftHandMesh) LeftHandMesh->SetVisibility(false);
		if (RightHandMesh) RightHandMesh->SetVisibility(false);
		if (CockpitDisplayWidget) CockpitDisplayWidget->SetVisibility(false);
		if (SpeedTextRender) SpeedTextRender->SetVisibility(false);
		if (PositionTextRender) PositionTextRender->SetVisibility(false);
		if (GearTextRender) GearTextRender->SetVisibility(false);
		if (PoliceAlertTextRender) PoliceAlertTextRender->SetVisibility(false);
		if (GearShiftLeverMesh) GearShiftLeverMesh->SetVisibility(false);
		if (GearShiftKnobMesh) GearShiftKnobMesh->SetVisibility(false);
		if (SteeringWheelVisualMesh) SteeringWheelVisualMesh->SetVisibility(false);
		if (SteeringColumnMesh) SteeringColumnMesh->SetVisibility(false);
		if (DashboardBackplateMesh) DashboardBackplateMesh->SetVisibility(false);
		if (DashboardWoodTrimMesh) DashboardWoodTrimMesh->SetVisibility(false);
		if (AmbientLightStripMesh) AmbientLightStripMesh->SetVisibility(false);
		if (CentralTouchscreenMesh) CentralTouchscreenMesh->SetVisibility(false);
		if (CentralScreenTitle) CentralScreenTitle->SetVisibility(false);
		if (CentralScreenDriveModes) CentralScreenDriveModes->SetVisibility(false);
		if (CentralScreenTacticalCopilot) CentralScreenTacticalCopilot->SetVisibility(false);
		if (CentralScreenBatteryNitro) CentralScreenBatteryNitro->SetVisibility(false);
		if (CentralScreenSubStatus) CentralScreenSubStatus->SetVisibility(false);
		if (EngineStartButtonMesh) EngineStartButtonMesh->SetVisibility(false);
		if (NitroButtonMesh) NitroButtonMesh->SetVisibility(false);
		if (BrakePedalMesh) BrakePedalMesh->SetVisibility(false);
		if (ThrottlePedalMesh) ThrottlePedalMesh->SetVisibility(false);

		AutoPossessPlayer = EAutoReceiveInput::Disabled;
		AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;

		if (!TrackActor.IsValid())
		{
			TrackActor = Cast<ARaceTrackSpline>(UGameplayStatics::GetActorOfClass(GetWorld(), ARaceTrackSpline::StaticClass()));
		}
		if (SplineFollower && TrackActor.IsValid())
		{
			SplineFollower->SetTargetSpline(TrackActor->GetSplineComponent());
			SplineFollower->TargetCruisingSpeedKmh = AiTargetSpeedKmh;
		}
	}

	// Dynamic Vehicle Livery Assignment (Player: Red, Rivals: Cyan/Lime/Gold/Purple, Police: Black)
	if (ChassisMeshComponent)
	{
		UMaterialInterface* ClearGlassMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Vehicles/Materials/M_TrueClearGlass.M_TrueClearGlass"));
		UMaterialInterface* BlackTrimMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Vehicles/Materials/M_SteeringWheel_Alcantara.M_SteeringWheel_Alcantara"));
		UMaterialInterface* ChromeMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Vehicles/Metal_-_Chrome.Metal_-_Chrome"));

		UMaterialInterface* LiveryPaint = nullptr;
		const FString SelfName = GetName();
		const bool bIsPoliceVehicle = SelfName.Contains(TEXT("Police")) || GetClass()->GetName().Contains(TEXT("Police"));

		if (bIsPoliceVehicle)
		{
			LiveryPaint = BlackTrimMat;
		}
		else if (!bIsAiRacer)
		{
			LiveryPaint = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Vehicles/Materials/M_Paint_Rosso_Corsa.M_Paint_Rosso_Corsa"));
		}
		else
		{
			if (SelfName.Contains(TEXT("Rival_01")) || SelfName.Contains(TEXT("1")))
			{
				LiveryPaint = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Vehicles/Materials/M_Paint_Cyan_Electric.M_Paint_Cyan_Electric"));
			}
			else if (SelfName.Contains(TEXT("Rival_02")) || SelfName.Contains(TEXT("2")))
			{
				LiveryPaint = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Vehicles/Materials/M_Paint_Lime_Sport.M_Paint_Lime_Sport"));
			}
			else if (SelfName.Contains(TEXT("Rival_03")) || SelfName.Contains(TEXT("3")))
			{
				LiveryPaint = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Vehicles/Materials/M_Paint_Gold_Hypercar.M_Paint_Gold_Hypercar"));
			}
			else
			{
				LiveryPaint = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Vehicles/Materials/M_Paint_Cyber_Purple.M_Paint_Cyber_Purple"));
			}
		}

		UMaterialInterface* TireMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Vehicles/Materials/M_VehicleTires.M_VehicleTires"));
		UMaterialInterface* RedTailLightMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Vehicles/Materials/M_Siren_Red.M_Siren_Red"));

		const int32 TotalMeshSlots = ChassisMeshComponent->GetNumMaterials();
		if (LiveryPaint)
		{
			// 1. Paint ALL slots with the rich car livery color by default (NO white checkerboard anywhere!)
			for (int32 SlotIdx = 0; SlotIdx < TotalMeshSlots; ++SlotIdx)
			{
				ChassisMeshComponent->SetMaterial(SlotIdx, LiveryPaint);
			}
		}

		// 2. High-clarity transparent glass for windshield and side windows (Slot 34 is the primary windshield)
		if (ClearGlassMat)
		{
			const int32 RealGlassSlots[] = {1, 16, 18, 19, 32, 34, 42, 43};
			for (int32 Slot : RealGlassSlots)
			{
				if (Slot < TotalMeshSlots)
				{
					ChassisMeshComponent->SetMaterial(Slot, ClearGlassMat);
				}
			}
		}

		// 3. Dark interior trim, dashboard, aero diffusers, and carbon accents
		if (BlackTrimMat)
		{
			const int32 TrimSlots[] = {2, 4, 7, 11, 21, 26, 27, 30, 39, 40, 41};
			for (int32 Slot : TrimSlots)
			{
				if (Slot < TotalMeshSlots)
				{
					ChassisMeshComponent->SetMaterial(Slot, BlackTrimMat);
				}
			}
		}

		// 4. Chrome accents (rims, exhaust pipes, badges)
		if (ChromeMat)
		{
			const int32 ChromeSlots[] = {0, 8, 12, 20, 24};
			for (int32 Slot : ChromeSlots)
			{
				if (Slot < TotalMeshSlots)
				{
					ChassisMeshComponent->SetMaterial(Slot, ChromeMat);
				}
			}
		}

		// 5. Tail lights (Slot 15)
		if (RedTailLightMat && 15 < TotalMeshSlots)
		{
			ChassisMeshComponent->SetMaterial(15, RedTailLightMat);
		}

		// 6. Real Rubber Tires (Slot 23)
		if (TireMat && 23 < TotalMeshSlots)
		{
			ChassisMeshComponent->SetMaterial(23, TireMat);
		}

		// Ensure steering wheel has black Alcantara trim on all slots (never white)
		if (SteeringWheelVisualMesh && BlackTrimMat)
		{
			for (int32 s = 0; s < 4; ++s)
			{
				SteeringWheelVisualMesh->SetMaterial(s, BlackTrimMat);
			}
		}
	}

	// Intelligent VR Headset vs Desktop Detection
	if (!bIsAiRacer)
	{
		const bool bIsHMDActive = UHeadMountedDisplayFunctionLibrary::IsHeadMountedDisplayEnabled();
		if (bIsHMDActive)
		{
			// Meta Quest / VR Headset: START IN COCKPIT WITH 6DOF VR TRACKING AND HAND CONTROLLERS
			ActiveCameraMode = 1; // 1 = Cockpit Camera (VR Headset Mode)
			if (VRCamera) VRCamera->SetActive(true);
			if (ChaseCamera) ChaseCamera->SetActive(false);
			if (HoodCamera) HoodCamera->SetActive(false);

			if (LeftMotionController) LeftMotionController->SetActive(true);
			if (RightMotionController) RightMotionController->SetActive(true);
			if (LeftHandMesh) LeftHandMesh->SetVisibility(true);
			if (RightHandMesh) RightHandMesh->SetVisibility(true);
		}
		else
		{
			// Desktop fallback (testing in editor without VR headset):
			ActiveCameraMode = 0; // 0 = Chase Camera for easy desktop preview, 'C' to switch
			if (ChaseCamera) ChaseCamera->SetActive(true);
			if (VRCamera) VRCamera->SetActive(false);
			if (HoodCamera) HoodCamera->SetActive(false);
		}
	}
	else
	{
		if (ChaseCamera) ChaseCamera->SetActive(false);
		if (HoodCamera) HoodCamera->SetActive(false);
	}

	// Initialize track progress and lateral offset from starting position
	RaceCountdownTimer = 3.99f;
	bIsRaceActive = false;
	LateralBounceVelocity = 0.0f;

	if (!TrackActor.IsValid())
	{
		TrackActor = Cast<ARaceTrackSpline>(UGameplayStatics::GetActorOfClass(GetWorld(), ARaceTrackSpline::StaticClass()));
	}
	if (TrackActor.IsValid() && TrackActor->GetSplineComponent())
	{
		USplineComponent* Spline = TrackActor->GetSplineComponent();
		const FVector MyLoc = GetActorLocation();
		const float MyKey = Spline->FindInputKeyClosestToWorldLocation(MyLoc);
		DistanceAlongTrack = Spline->GetDistanceAlongSplineAtSplineInputKey(MyKey);
		const FVector Center = Spline->GetLocationAtSplineInputKey(MyKey, ESplineCoordinateSpace::World);
		const FVector RightVec = Spline->GetRightVectorAtSplineInputKey(MyKey, ESplineCoordinateSpace::World);
		LateralTrackOffset = FVector::DotProduct(MyLoc - Center, RightVec);
	}
}

void AVrVehiclePawn::CycleCameraMode()
{
	if (bIsAiRacer)
	{
		return;
	}

	ActiveCameraMode = (ActiveCameraMode + 1) % 3;

	if (ActiveCameraMode == 0)
	{
		// Chase Camera (Third Person Arcade View)
		if (ChaseCamera) ChaseCamera->SetActive(true);
		if (VRCamera) VRCamera->SetActive(false);
		if (HoodCamera) HoodCamera->SetActive(false);
		if (GEngine) GEngine->AddOnScreenDebugMessage(99, 2.5f, FColor(0, 245, 255), TEXT(">>> CAMERA: CHASE CAM (ARCADE) [C] <<<"), true, FVector2D(1.4f, 1.4f));
	}
	else if (ActiveCameraMode == 1)
	{
		// Cockpit Camera (First Person Driver View)
		if (ChaseCamera) ChaseCamera->SetActive(false);
		if (VRCamera) VRCamera->SetActive(true);
		if (HoodCamera) HoodCamera->SetActive(false);
		if (GEngine) GEngine->AddOnScreenDebugMessage(99, 2.5f, FColor(255, 215, 0), TEXT(">>> CAMERA: COCKPIT VIEW [C] <<<"), true, FVector2D(1.4f, 1.4f));
	}
	else
	{
		// Hood / Bumper Camera (Clear Forward Track View)
		if (ChaseCamera) ChaseCamera->SetActive(false);
		if (VRCamera) VRCamera->SetActive(false);
		if (HoodCamera) HoodCamera->SetActive(true);
		if (GEngine) GEngine->AddOnScreenDebugMessage(99, 2.5f, FColor(0, 255, 128), TEXT(">>> CAMERA: HOOD CAM [C] <<<"), true, FVector2D(1.4f, 1.4f));
	}
}

void AVrVehiclePawn::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	UpdateCockpitTelemetry(DeltaTime);

	// Animate Sequential Gear Shifter Lever (Caja de cambios)
	if (GearShiftLeverMesh)
	{
		float ShiftPitchOffset = 0.0f;
		if (GearShiftAnimProgress < 1.0f)
		{
			GearShiftAnimProgress = FMath::Min(1.0f, GearShiftAnimProgress + DeltaTime * 4.5f);
			// Flick forward and snap back (Sine wave mechanical impulse)
			ShiftPitchOffset = FMath::Sin(GearShiftAnimProgress * PI) * 16.0f;
		}
		GearShiftLeverMesh->SetRelativeRotation(FRotator(-12.0f + ShiftPitchOffset, 0.0f, 0.0f));
	}

	// Update Nitro state and consumption
	if (bIsNitroActive && NitroAmount > 0.0f)
	{
		NitroAmount = FMath::Max(0.0f, NitroAmount - NitroDepletionRate * DeltaTime);
		if (NitroAmount <= 0.0f)
		{
			bIsNitroActive = false;
		}

		if (ChaosMovementComp && CurrentRawThrottle > 0.0f)
		{
			ChaosMovementComp->SetThrottleInput(FMath::Clamp(CurrentRawThrottle * NitroBoostMultiplier, 0.0f, 1.0f));
		}
	}
	else if (!bIsNitroActive && NitroAmount < 100.0f)
	{
		NitroAmount = FMath::Min(100.0f, NitroAmount + NitroRechargeRate * DeltaTime);
	}

	// Update visual nitro exhaust flames & light
	if (LeftNitroFlameMesh && RightNitroFlameMesh)
	{
		LeftNitroFlameMesh->SetVisibility(bIsNitroActive);
		RightNitroFlameMesh->SetVisibility(bIsNitroActive);
		if (NitroFlameLight)
		{
			NitroFlameLight->SetVisibility(bIsNitroActive);
		}
		if (bIsNitroActive)
		{
			const float FlamePulse = FMath::FRandRange(0.85f, 1.25f);
			LeftNitroFlameMesh->SetRelativeScale3D(FVector(0.12f, 0.12f, 0.38f * FlamePulse));
			RightNitroFlameMesh->SetRelativeScale3D(FVector(0.12f, 0.12f, 0.38f * FlamePulse));
		}
	}

	// Audio modulation - Deep supercar rumble, smooth & pleasant (never screeching or tiring)
	if (EngineAudioComponent)
	{
		const float Pitch = FMath::Clamp(0.62f + (GetSpeedKmh() / 280.0f) * 0.38f, 0.60f, 1.02f);
		EngineAudioComponent->SetPitchMultiplier(Pitch);
		const float Volume = bIsAiRacer ? 0.07f : (bIsNitroActive ? 0.22f : 0.20f);
		EngineAudioComponent->SetVolumeMultiplier(Volume);
	}

	// Desktop PIE Keyboard Controls (W/S/A/D / Arrows / Space / N)
	APlayerController* PC = Cast<APlayerController>(GetController());
	if (!PC)
	{
		PC = UGameplayStatics::GetPlayerController(GetWorld(), 0);
	}

	if (PC && !bIsAiRacer)
	{
		float ForwardInput = 0.0f;
		float SteerInput = 0.0f;

		if (PC->IsInputKeyDown(EKeys::W) || PC->IsInputKeyDown(EKeys::Up))
		{
			ForwardInput += 1.0f;
		}
		if (PC->IsInputKeyDown(EKeys::S) || PC->IsInputKeyDown(EKeys::Down))
		{
			ForwardInput -= 1.0f;
		}

		if (PC->IsInputKeyDown(EKeys::D) || PC->IsInputKeyDown(EKeys::Right))
		{
			SteerInput += 1.0f;
		}
		if (PC->IsInputKeyDown(EKeys::A) || PC->IsInputKeyDown(EKeys::Left))
		{
			SteerInput -= 1.0f;
		}

		const bool bNitroPressed = PC->IsInputKeyDown(EKeys::SpaceBar) || PC->IsInputKeyDown(EKeys::N) || PC->IsInputKeyDown(EKeys::LeftShift);
		ActivateNitro(bNitroPressed);

		// Key C or V toggles camera (Third-person chase cam <-> Cockpit <-> Hood)
		if (PC->WasInputKeyJustPressed(EKeys::C) || PC->WasInputKeyJustPressed(EKeys::V))
		{
			CycleCameraMode();
		}

		// Key R or Enter or Gamepad Face Button restarts race
		if (PC->WasInputKeyJustPressed(EKeys::R) ||
		    (bIsBusted && (PC->WasInputKeyJustPressed(EKeys::Enter) ||
		                   PC->WasInputKeyJustPressed(EKeys::Gamepad_FaceButton_Bottom) ||
		                   PC->WasInputKeyJustPressed(EKeys::SpaceBar))))
		{
			RestartRace();
		}

		// Key M toggles in-game background music on/off
		if (PC->WasInputKeyJustPressed(EKeys::M))
		{
			ToggleMusic();
		}

		if (PC->IsInputKeyDown(EKeys::E))
		{
			// Tap E to toggle engine
			static float LastToggleTime = 0.0f;
			const float CurrTime = GetWorld()->GetTimeSeconds();
			if (CurrTime - LastToggleTime > 0.5f)
			{
				LastToggleTime = CurrTime;
				ToggleEngine();
			}
		}

		if (ForwardInput > 0.0f)
		{
			SetThrottle(ForwardInput);
			SetBrake(0.0f);
		}
		else if (ForwardInput < 0.0f)
		{
			SetThrottle(0.0f);
			SetBrake(FMath::Abs(ForwardInput));
		}
		else if (!SteeringWheelComponent || (!SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Left) && !SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Right)))
		{
			SetThrottle(0.0f);
			SetBrake(0.0f);
		}

		// Comprehensive Steering Blend (Keyboard + Controller Thumbstick + Motion Hands)
		float EffectiveSteer = SteerInput;
		if (FMath::Abs(AxisSteerInput) > 0.04f)
		{
			EffectiveSteer = AxisSteerInput;
		}

		if (FMath::Abs(EffectiveSteer) > 0.01f)
		{
			CurrentSteeringInput = FMath::FInterpTo(CurrentSteeringInput, EffectiveSteer, DeltaTime, 28.0f);
		}
		else if (!SteeringWheelComponent || (!SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Left) && !SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Right)))
		{
			CurrentSteeringInput = FMath::FInterpTo(CurrentSteeringInput, 0.0f, DeltaTime, 18.0f);
		}

		// Synchronize visual 3D cockpit steering wheel angle smoothly and visibly
		if (SteeringWheelComponent && !SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Left) && !SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Right))
		{
			SteeringWheelComponent->SetSteeringAngleDeg(CurrentSteeringInput * 110.0f);
		}

		if (ChaosMovementComp)
		{
			ChaosMovementComp->SetSteeringInput(CurrentSteeringInput);
		}
	}

	// Hands-First VR Proximity Auto-Grab & Hands Interactions
	if (!bIsAiRacer && SteeringWheelComponent)
	{
		// 1. Left Hand Steering Grab
		USceneComponent* LeftComp = LeftHandMesh ? (USceneComponent*)LeftHandMesh : (USceneComponent*)LeftMotionController;
		if (LeftComp)
		{
			const bool bInRange = SteeringWheelComponent->IsInGrabRange(LeftComp);
			if (bInRange && !SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Left))
			{
				SteeringWheelComponent->StartSteering(EVrHandSide::Left, LeftComp);
			}
			else if (!bInRange && SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Left))
			{
				const FVector LocalPos = SteeringWheelComponent->GetComponentTransform().InverseTransformPosition(LeftComp->GetComponentLocation());
				const float RadialDist = FMath::Sqrt(LocalPos.Y * LocalPos.Y + LocalPos.Z * LocalPos.Z);
				const float DistToRim = FMath::Sqrt(FMath::Square(RadialDist - SteeringWheelComponent->WheelRimRadius) + FMath::Square(LocalPos.X));
				if (DistToRim > (SteeringWheelComponent->GrabRadius + 8.0f))
				{
					SteeringWheelComponent->StopSteering(EVrHandSide::Left);
				}
			}
		}

		// 2. Right Hand Steering Grab
		USceneComponent* RightComp = RightHandMesh ? (USceneComponent*)RightHandMesh : (USceneComponent*)RightMotionController;
		if (RightComp)
		{
			const bool bInRange = SteeringWheelComponent->IsInGrabRange(RightComp);
			if (bInRange && !SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Right))
			{
				SteeringWheelComponent->StartSteering(EVrHandSide::Right, RightComp);
			}
			else if (!bInRange && SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Right))
			{
				const FVector LocalPos = SteeringWheelComponent->GetComponentTransform().InverseTransformPosition(RightComp->GetComponentLocation());
				const float RadialDist = FMath::Sqrt(LocalPos.Y * LocalPos.Y + LocalPos.Z * LocalPos.Z);
				const float DistToRim = FMath::Sqrt(FMath::Square(RadialDist - SteeringWheelComponent->WheelRimRadius) + FMath::Square(LocalPos.X));
				if (DistToRim > (SteeringWheelComponent->GrabRadius + 8.0f))
				{
					SteeringWheelComponent->StopSteering(EVrHandSide::Right);
				}
			}

			// 3. Hands-First Touch Nitro Button
			if (NitroButtonMesh)
			{
				const float DistToNitro = FVector::Dist(RightComp->GetComponentLocation(), NitroButtonMesh->GetComponentLocation());
				if (DistToNitro < 10.0f)
				{
					ActivateNitro(true);
				}
			}
		}

		// If hands are gripping the wheel, wheel angle directly drives vehicle steering!
		if (SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Left) || SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Right))
		{
			CurrentSteeringInput = SteeringWheelComponent->GetNormalizedSteering();
		}
	}

	// AI Rival Racer Logic
	if (bIsAiRacer)
	{
		if (!TrackActor.IsValid())
		{
			TrackActor = Cast<ARaceTrackSpline>(UGameplayStatics::GetActorOfClass(GetWorld(), ARaceTrackSpline::StaticClass()));
			if (SplineFollower && TrackActor.IsValid())
			{
				SplineFollower->SetTargetSpline(TrackActor->GetSplineComponent());
				SplineFollower->TargetCruisingSpeedKmh = AiTargetSpeedKmh;
			}
		}

		if (SplineFollower && SplineFollower->HasValidSpline())
		{
			float Steer = 0.0f, Throttle = 0.0f, Brake = 0.0f;
			SplineFollower->ComputeSteeringAndThrottle(GetSpeedKmh(), Steer, Throttle, Brake);
			CurrentSteeringInput = Steer;
			CurrentRawThrottle = Throttle;
			if (ChaosMovementComp)
			{
				ChaosMovementComp->SetSteeringInput(Steer);
				ChaosMovementComp->SetThrottleInput(Throttle);
				ChaosMovementComp->SetBrakeInput(Brake);
			}
		}
	}

	// Dynamic Kinematic Track-Bound Movement with Real Cornering Inertia and Driver Steering Authority
	{
		float EffectiveThrottle = CurrentRawThrottle;
		if (bIsNitroActive)
		{
			EffectiveThrottle *= NitroBoostMultiplier;
		}

		if (!bIsRaceActive)
		{
			EffectiveThrottle = 0.0f;
			FallbackSpeedKmh = 0.0f;
		}
		else if (EffectiveThrottle > 0.01f)
		{
			const float MaxSpeed = bIsNitroActive ? 280.0f : 220.0f;
			const float AccelRate = bIsNitroActive ? 180.0f : 95.0f;
			if (FallbackSpeedKmh > MaxSpeed)
			{
				FallbackSpeedKmh = FMath::FInterpTo(FallbackSpeedKmh, MaxSpeed, DeltaTime, 2.5f);
			}
			else
			{
				FallbackSpeedKmh = FMath::Min(FallbackSpeedKmh + AccelRate * DeltaTime * EffectiveThrottle, MaxSpeed);
			}
		}
		else
		{
			FallbackSpeedKmh = FMath::FInterpTo(FallbackSpeedKmh, 0.0f, DeltaTime, 1.2f);
		}

		if (ChaosMovementComp && ChaosMovementComp->GetBrakeInput() > 0.01f)
		{
			const float BrakeVal = ChaosMovementComp->GetBrakeInput();
			if (FallbackSpeedKmh > 1.0f)
			{
				FallbackSpeedKmh = FMath::Max(FallbackSpeedKmh - 160.0f * DeltaTime * BrakeVal, 0.0f);
			}
			else
			{
				// Reverse gear when stopped
				FallbackSpeedKmh = FMath::Max(FallbackSpeedKmh - 45.0f * DeltaTime * BrakeVal, -35.0f);
			}
		}

		if (!TrackActor.IsValid())
		{
			TrackActor = Cast<ARaceTrackSpline>(UGameplayStatics::GetActorOfClass(GetWorld(), ARaceTrackSpline::StaticClass()));
		}

		if (TrackActor.IsValid() && TrackActor->GetSplineComponent())
		{
			USplineComponent* Spline = TrackActor->GetSplineComponent();
			const float SplineLen = Spline->GetSplineLength();

			// 1. Advance along track circuit based on forward speed
			const float MoveDeltaDist = (FallbackSpeedKmh * (100.0f / 3.6f)) * DeltaTime;
			DistanceAlongTrack += MoveDeltaDist;
			if (SplineLen > 100.0f)
			{
				DistanceAlongTrack = FMath::Fmod(DistanceAlongTrack, SplineLen);
				if (DistanceAlongTrack < 0.0f)
				{
					DistanceAlongTrack += SplineLen;
				}
			}

			// Lap completion detection (crossing start/finish line)
			if (bIsRaceActive && SplineLen > 1000.0f)
			{
				if (PreviousDistanceAlongTrack > (SplineLen * 0.65f) && DistanceAlongTrack < (SplineLen * 0.35f))
				{
					CurrentLap++;
					if (!bIsAiRacer)
					{
						TriggerHapticFeedback(0.7f, 0.3f, true, true);
						if (CurrentLap > TotalLaps)
						{
							bRaceFinished = true;
							CurrentLap = TotalLaps;
						}
					}
				}
				PreviousDistanceAlongTrack = DistanceAlongTrack;
			}

			if (bIsAiRacer)
			{
				if (!bIsRaceActive)
				{
					AVrVehiclePawn* PlayerPawn = Cast<AVrVehiclePawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
					if (PlayerPawn && PlayerPawn->bIsRaceActive)
					{
						bIsRaceActive = true;
					}
				}

				// DYNAMIC HUMAN-LIKE RACING LINES FOR AI RIVALS (Organic, Individual, Non-conforming)
				float BaseLane = 0.0f;
				const FString SelfName = GetName();
				const float TimeSec = GetWorld()->GetTimeSeconds();

				// Road Curvature for apex clipping
				const float CurvLookahead = 800.0f;
				const FVector CurDir = Spline->GetDirectionAtDistanceAlongSpline(DistanceAlongTrack, ESplineCoordinateSpace::World);
				const FVector AheadDir = Spline->GetDirectionAtDistanceAlongSpline(DistanceAlongTrack + CurvLookahead, ESplineCoordinateSpace::World);
				const float RoadYawDelta = FMath::FindDeltaAngleDegrees(CurDir.Rotation().Yaw, AheadDir.Rotation().Yaw);
				const float RoadCurvature = RoadYawDelta / (CurvLookahead / 100.0f);

				// Apex displacement: when turning right (YawDelta > 0), inside apex is right (+); when turning left, inside apex is left (-)
				const float ApexOffset = FMath::Clamp(RoadCurvature * 110.0f, -190.0f, 190.0f);

				if (SelfName.Contains(TEXT("Rival_01")) || SelfName.Contains(TEXT("1")))
				{
					// Rival 1 (Cyan): Apex champion & Grand Prix Leader - 238 km/h!
					BaseLane = -160.0f + ApexOffset + FMath::Sin(TimeSec * 0.45f) * 35.0f;
					AiTargetSpeedKmh = 238.0f;
				}
				else if (SelfName.Contains(TEXT("Rival_02")) || SelfName.Contains(TEXT("2")))
				{
					// Rival 2 (Green): High-speed outside sweeper - 228 km/h!
					BaseLane = 220.0f - (ApexOffset * 0.5f) + FMath::Cos(TimeSec * 0.38f) * 45.0f;
					AiTargetSpeedKmh = 228.0f;
				}
				else if (SelfName.Contains(TEXT("Rival_03")) || SelfName.Contains(TEXT("3")))
				{
					// Rival 3 (Purple): Aggressive overtaker - 220 km/h!
					BaseLane = 30.0f + (ApexOffset * 0.6f) + FMath::Sin(TimeSec * 0.65f) * 65.0f;
					AiTargetSpeedKmh = 220.0f;
				}
				else
				{
					BaseLane = -60.0f + FMath::Sin(TimeSec * 0.5f) * 50.0f;
					AiTargetSpeedKmh = 216.0f;
				}

				// Dynamic AI competitive behaviors:
				AVrVehiclePawn* PlayerPawnRef = Cast<AVrVehiclePawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
				if (PlayerPawnRef && PlayerPawnRef != this)
				{
					float PlayerLeadDist = PlayerPawnRef->DistanceAlongTrack - DistanceAlongTrack;
					if (Spline->IsClosedLoop())
					{
						if (PlayerLeadDist < -SplineLen * 0.5f) PlayerLeadDist += SplineLen;
						else if (PlayerLeadDist > SplineLen * 0.5f) PlayerLeadDist -= SplineLen;
					}

					// 1. DEFENSIVE OVERBOOST: Player is closing in from behind (-35m to 0m)
					if (PlayerLeadDist >= -3500.0f && PlayerLeadDist < 0.0f)
					{
						AiTargetSpeedKmh += 18.0f; // Rivals fight for position! Player needs Nitro to overtake!
					}
					// 2. SLIPSTREAM PURSUIT: Player has passed ahead (0m to 100m)
					else if (PlayerLeadDist >= 0.0f && PlayerLeadDist < 10000.0f)
					{
						AiTargetSpeedKmh += 24.0f; // Aggressive slipstream pursuit boost!
					}
				}

				if (!bIsRaceActive)
				{
					FallbackSpeedKmh = 0.0f;
				}
				else
				{
					// High-torque launch & snappy acceleration (3.2f)
					FallbackSpeedKmh = FMath::FInterpTo(FallbackSpeedKmh, AiTargetSpeedKmh, DeltaTime, 3.2f);
				}

				// AI Proactive Overtaking: look 25 meters (2500cm) ahead!
				// If any vehicle is ahead in the same path, smoothly change lanes well before contact
				for (TActorIterator<AVrVehiclePawn> It(GetWorld()); It; ++It)
				{
					AVrVehiclePawn* OtherPawn = *It;
					if (OtherPawn && OtherPawn != this)
					{
						float DistDiff = OtherPawn->DistanceAlongTrack - DistanceAlongTrack;
						if (DistDiff < -SplineLen * 0.5f) DistDiff += SplineLen;
						else if (DistDiff > SplineLen * 0.5f) DistDiff -= SplineLen;

						const float LateralDiff = OtherPawn->LateralTrackOffset - LateralTrackOffset;

						if (DistDiff > 80.0f && DistDiff < 2500.0f && FMath::Abs(LateralDiff) < 220.0f)
						{
							if (LateralTrackOffset <= 0.0f)
							{
								BaseLane += 260.0f;
							}
							else
							{
								BaseLane -= 260.0f;
							}
							break;
						}
					}
				}

				BaseLane = FMath::Clamp(BaseLane, -480.0f, 480.0f);
				LateralTrackOffset = FMath::FInterpTo(LateralTrackOffset, BaseLane, DeltaTime, 2.0f);
			}
			else
			{
				// 3. ULTRA-RESPONSIVE PLAYER STEERING (100% Free Driver Authority, Direct & Unhindered):
				// BaseSteeringSpeed at 2400 cm/s (24 meters per second lateral speed!)
				const float BaseSteeringSpeed = 2400.0f;
				// Full authority at ANY speed (even when stopped or slow!)
				const float SpeedFactor = FMath::Clamp(FallbackSpeedKmh / 40.0f, 0.90f, 1.30f);
				const float PlayerSteeringDisplacement = CurrentSteeringInput * BaseSteeringSpeed * SpeedFactor * DeltaTime;

				// Direct 1:1 steering input: no artificial centrifugal drift locking or fighting the wheel!
				LateralTrackOffset += PlayerSteeringDisplacement;

				// 4. Smooth, Non-Sticky Guardrail Containment:
				// Road half-width is 700cm; guardrail inner edge is at ~560cm.
				const float MaxTrackLimit = 560.0f;
				if (LateralTrackOffset > MaxTrackLimit)
				{
					LateralTrackOffset = MaxTrackLimit;
					TriggerHapticFeedback(0.25f, 0.05f, false, true);
				}
				else if (LateralTrackOffset < -MaxTrackLimit)
				{
					LateralTrackOffset = -MaxTrackLimit;
					TriggerHapticFeedback(0.25f, 0.05f, true, false);
				}

				// 5. Slipstream / Drafting & Pure Lateral Vehicle-to-Vehicle Collisions with Rivals
				bool bInSlipstream = false;
				bool bVehicleCollision = false;
				const float MinCarDist = 380.0f;
				const float MinLateralDist = 190.0f;

				for (TActorIterator<AVrVehiclePawn> It(GetWorld()); It; ++It)
				{
					AVrVehiclePawn* OtherPawn = *It;
					if (OtherPawn && OtherPawn != this)
					{
						float DistDiff = OtherPawn->DistanceAlongTrack - DistanceAlongTrack;
						if (DistDiff < -SplineLen * 0.5f) DistDiff += SplineLen;
						else if (DistDiff > SplineLen * 0.5f) DistDiff -= SplineLen;

						const float LateralDiff = OtherPawn->LateralTrackOffset - LateralTrackOffset;

						// Vehicle-to-Vehicle Lateral Bump & Repulsion (NEVER lock or freeze DistanceAlongTrack!)
						if (FMath::Abs(DistDiff) < MinCarDist && FMath::Abs(LateralDiff) < MinLateralDist)
						{
							bVehicleCollision = true;
							TriggerHapticFeedback(0.55f, 0.12f, true, true);

							// Push apart laterally so player can freely weave past
							const float LateralOverlap = MinLateralDist - FMath::Abs(LateralDiff);
							const float SepSign = (LateralDiff >= 0.0f) ? -1.0f : 1.0f;
							LateralTrackOffset += SepSign * (LateralOverlap * 0.65f);
							OtherPawn->LateralTrackOffset -= SepSign * (LateralOverlap * 0.35f);

							// Slight speed bump (transfer forward momentum without stopping)
							if (DistDiff > 0.0f)
							{
								FallbackSpeedKmh = FMath::Max(50.0f, FallbackSpeedKmh - 15.0f * DeltaTime * 6.0f);
								OtherPawn->FallbackSpeedKmh = FMath::Min(215.0f, OtherPawn->FallbackSpeedKmh + 20.0f);
							}
							else
							{
								FallbackSpeedKmh = FMath::Min(230.0f, FallbackSpeedKmh + 15.0f);
							}

							if (PoliceAlertTextRender)
							{
								PoliceAlertTextRender->SetText(FText::FromString(TEXT("RIVAL CONTACT! - OVERTAKE ON OUTSIDE")));
								PoliceAlertTextRender->SetTextRenderColor(FColor(0, 245, 255));
							}
						}
						// Slipstream / Drafting behind Rival Ahead (within 14m, same lane)
						else if (DistDiff > 0.0f && DistDiff < 1400.0f && FMath::Abs(LateralDiff) < 140.0f)
						{
							bInSlipstream = true;
						}
					}
				}

				// Physical Bump with Police Interceptors (Pure Lateral Repulsion & Shove, NO STICKING!)
				const float MinPoliceDist = 400.0f;
				const float MinPoliceLateral = 195.0f;

				for (TActorIterator<APoliceVehiclePawn> It(GetWorld()); It; ++It)
				{
					APoliceVehiclePawn* PolicePawn = *It;
					if (PolicePawn)
					{
						float DistDiff = PolicePawn->DistanceAlongTrack - DistanceAlongTrack;
						if (DistDiff < -SplineLen * 0.5f) DistDiff += SplineLen;
						else if (DistDiff > SplineLen * 0.5f) DistDiff -= SplineLen;

						const float LateralDiff = PolicePawn->LateralTrackOffset - LateralTrackOffset;

						if (FMath::Abs(DistDiff) < MinPoliceDist && FMath::Abs(LateralDiff) < MinPoliceLateral)
						{
							bVehicleCollision = true;
							TriggerHapticFeedback(0.70f, 0.15f, true, true);

							// Lateral shove (PIT bump)
							const float LateralOverlap = MinPoliceLateral - FMath::Abs(LateralDiff);
							const float PushDir = (LateralDiff >= 0.0f) ? -1.0f : 1.0f;
							LateralTrackOffset += PushDir * (LateralOverlap * 0.70f);

							FallbackSpeedKmh = FMath::Max(45.0f, FallbackSpeedKmh - 20.0f * DeltaTime * 4.0f);

							if (PoliceAlertTextRender)
							{
								PoliceAlertTextRender->SetText(FText::FromString(TEXT("[!] POLICE ALONGSIDE! - ENGAGE NITRO")));
								PoliceAlertTextRender->SetTextRenderColor(FColor(255, 170, 0));
							}
						}
					}
				}

				if (bInSlipstream && !bVehicleCollision)
				{
					// Aerodynamic draft boost (+35 km/h acceleration)
					FallbackSpeedKmh = FMath::Min(240.0f, FallbackSpeedKmh + 40.0f * DeltaTime);
				}
			}

			// 7. Compute Target World Transform flush with asphalt surface (0.0cm ride height)
			const FVector SplinePos = Spline->GetLocationAtDistanceAlongSpline(DistanceAlongTrack, ESplineCoordinateSpace::World);
			const FVector SplineDir = Spline->GetDirectionAtDistanceAlongSpline(DistanceAlongTrack, ESplineCoordinateSpace::World);
			const FVector SplineRight = Spline->GetRightVectorAtDistanceAlongSpline(DistanceAlongTrack, ESplineCoordinateSpace::World);

			FVector TargetLocation = SplinePos + (SplineRight * LateralTrackOffset);

			// Dynamic Heading & Body Roll:
			const FRotator SplineRot = SplineDir.Rotation();
			// AI cars follow spline smoothly; player gets natural realistic turn angle (18 deg max) and body lean (-6.5 deg)
			const float DynamicYaw = bIsAiRacer ? SplineRot.Yaw : (SplineRot.Yaw + (CurrentSteeringInput * 18.0f));
			const float DynamicPitch = SplineRot.Pitch;
			const float DynamicRoll = bIsAiRacer ? 0.0f : (CurrentSteeringInput * -6.5f);
			FRotator TargetRotation(DynamicPitch, DynamicYaw, DynamicRoll);

			if (TrackActor.IsValid())
			{
				TrackActor->ClampVehicleToTrack(TargetLocation, TargetRotation, DeltaTime, 100.0f, 0.0f);
			}

			SetActorLocationAndRotation(TargetLocation, TargetRotation);
		}
		else
		{
			// Basic fallback if track actor missing
			if (FMath::Abs(FallbackSpeedKmh) > 0.1f)
			{
				const float TurnDelta = CurrentSteeringInput * 65.0f * DeltaTime;
				AddActorWorldRotation(FRotator(0.0f, TurnDelta, 0.0f), true);
				AddActorWorldOffset(GetActorForwardVector() * (FallbackSpeedKmh * (100.0f / 3.6f) * DeltaTime), true);
			}
		}
	}
}

void AVrVehiclePawn::UpdateCockpitTelemetry(float DeltaTime)
{
	if (bIsAiRacer)
	{
		return;
	}

	// 1. Race Countdown Phase (3, 2, 1, GO!)
	if (!bIsRaceActive)
	{
		RaceCountdownTimer -= DeltaTime;

		if (GEngine)
		{
			FString CountMsg;
			FColor CColor = FColor::White;
			if (RaceCountdownTimer > 3.0f) { CountMsg = TEXT("  [ 3 ]  "); CColor = FColor(255, 40, 40); }
			else if (RaceCountdownTimer > 2.0f) { CountMsg = TEXT("  [ 2 ]  "); CColor = FColor(255, 160, 0); }
			else if (RaceCountdownTimer > 1.0f) { CountMsg = TEXT("  [ 1 ]  "); CColor = FColor(255, 230, 0); }
			else { CountMsg = TEXT(">>> GO! FULL THROTTLE (W)! <<<"); CColor = FColor(0, 255, 128); }

			GEngine->AddOnScreenDebugMessage(100, 0.15f, CColor, CountMsg, true, FVector2D(2.6f, 2.6f));
		}

		if (GearTextRender)
		{
			GearTextRender->SetText(FText::FromString(TEXT("READY")));
			GearTextRender->SetTextRenderColor(FColor(255, 180, 0));
		}
		if (PositionTextRender)
		{
			PositionTextRender->SetText(FText::FromString(TEXT("GRID")));
			PositionTextRender->SetTextRenderColor(FColor(0, 245, 255));
		}

		if (SpeedTextRender)
		{
			if (RaceCountdownTimer > 3.0f)
			{
				SpeedTextRender->SetText(FText::FromString(TEXT("  3  ")));
				SpeedTextRender->SetTextRenderColor(FColor(255, 40, 40));
				SpeedTextRender->SetWorldSize(6.2f);
				if (PoliceAlertTextRender)
				{
					PoliceAlertTextRender->SetText(FText::FromString(TEXT("/// START ENGINES ///")));
					PoliceAlertTextRender->SetTextRenderColor(FColor(255, 60, 60));
				}
			}
			else if (RaceCountdownTimer > 2.0f)
			{
				SpeedTextRender->SetText(FText::FromString(TEXT("  2  ")));
				SpeedTextRender->SetTextRenderColor(FColor(255, 160, 0));
				SpeedTextRender->SetWorldSize(6.2f);
				if (PoliceAlertTextRender)
				{
					PoliceAlertTextRender->SetText(FText::FromString(TEXT("/// REV ENGINES ///")));
					PoliceAlertTextRender->SetTextRenderColor(FColor(255, 180, 0));
				}
			}
			else if (RaceCountdownTimer > 1.0f)
			{
				SpeedTextRender->SetText(FText::FromString(TEXT("  1  ")));
				SpeedTextRender->SetTextRenderColor(FColor(255, 230, 0));
				SpeedTextRender->SetWorldSize(6.2f);
				if (PoliceAlertTextRender)
				{
					PoliceAlertTextRender->SetText(FText::FromString(TEXT("/// READY TO LAUNCH ///")));
					PoliceAlertTextRender->SetTextRenderColor(FColor(255, 230, 0));
				}
			}
			else if (RaceCountdownTimer > 0.0f)
			{
				SpeedTextRender->SetText(FText::FromString(TEXT(" GO! ")));
				SpeedTextRender->SetTextRenderColor(FColor(0, 255, 128));
				SpeedTextRender->SetWorldSize(6.8f);
				if (PoliceAlertTextRender)
				{
					PoliceAlertTextRender->SetText(FText::FromString(TEXT(">>> FULL THROTTLE (W)! GO! GO! <<<")));
					PoliceAlertTextRender->SetTextRenderColor(FColor(0, 255, 128));
				}
			}
			else
			{
				bIsRaceActive = true;
				SpeedTextRender->SetWorldSize(3.6f);
				SpeedTextRender->SetTextRenderColor(FColor(0, 245, 255));

				// Broadcast race start to all AI racers on track!
				for (TActorIterator<AVrVehiclePawn> It(GetWorld()); It; ++It)
				{
					if (*It)
					{
						(*It)->bIsRaceActive = true;
					}
				}
			}
		}

		if (!bIsRaceActive)
		{
			return;
		}
	}

	const float Speed = GetSpeedKmh();

	if (GEngine)
	{
		FString HudStr;
		if (bRaceFinished)
		{
			if (CurrentRacePosition == 1)
			{
				HudStr = TEXT(">>> ★ VICTORY! YOU WIN! 1ST PLACE CHAMPION! ★  |  PRESS [R] TO RESTART <<<");
			}
			else
			{
				HudStr = FString::Printf(TEXT(">>> RACE FINISHED! FINAL POSITION: P%d / 7  |  PRESS [R] TO RESTART <<<"), CurrentRacePosition);
			}
		}
		else
		{
			HudStr = FString::Printf(TEXT("POS: P%d / 7  |  LAP: %d / %d  |  %d KM/H  |  GEAR: %d  |  NITRO: %d%%  |  [C] CHANGE CAMERA"),
				CurrentRacePosition, CurrentLap, TotalLaps, FMath::RoundToInt(Speed), CurrentGear, FMath::RoundToInt(GetNitroPercentage()));
		}
		GEngine->AddOnScreenDebugMessage(101, 0.15f, bRaceFinished ? (CurrentRacePosition == 1 ? FColor(255, 215, 0) : FColor(0, 255, 128)) : FColor(0, 245, 255), HudStr, true, FVector2D(1.4f, 1.4f));
	}

	// Compute realistic automatic gear based on speed
	const int32 NewGear = (Speed < 35.0f) ? 1 :
	                      (Speed < 70.0f) ? 2 :
	                      (Speed < 105.0f) ? 3 :
	                      (Speed < 145.0f) ? 4 :
	                      (Speed < 185.0f) ? 5 : 6;

	if (NewGear != CurrentGear)
	{
		CurrentGear = NewGear;
		GearShiftAnimProgress = 0.0f; // Triggers sequential gear shifter lever animation!
	}

	if (SpeedTextRender)
	{
		SpeedTextRender->SetText(FText::FromString(FString::Printf(TEXT("%d KM/H"), FMath::RoundToInt(Speed))));
	}

	if (GearTextRender)
	{
		GearTextRender->SetText(FText::FromString(FString::Printf(TEXT("GEAR: %d"), CurrentGear)));
	}

	// Update Rivian Central Screen Battery / Nitro status
	if (CentralScreenBatteryNitro)
	{
		const int32 NitroPct = FMath::Clamp(FMath::RoundToInt(NitroAmount), 0, 100);
		const FString BoostState = bIsNitroActive ? TEXT(">>> BOOST ACTIVE <<<") : (NitroPct > 25 ? TEXT("[ READY ]") : TEXT("[ RECHARGING ]"));
		CentralScreenBatteryNitro->SetText(FText::FromString(FString::Printf(TEXT("EV BATTERY: %d%%  ||  NITRO: %s"), NitroPct, *BoostState)));
		if (bIsNitroActive)
		{
			CentralScreenBatteryNitro->SetTextRenderColor(FColor(0, 255, 255));
		}
		else if (NitroPct < 25)
		{
			CentralScreenBatteryNitro->SetTextRenderColor(FColor(255, 140, 0));
		}
		else
		{
			CentralScreenBatteryNitro->SetTextRenderColor(FColor(255, 215, 0));
		}
	}

	TelemetryUpdateTimer += DeltaTime;
	if (TelemetryUpdateTimer >= 0.2f)
	{
		TelemetryUpdateTimer = 0.0f;
		UpdateRacePosition();
	}
}

void AVrVehiclePawn::UpdateRacePosition()
{
	if (!TrackActor.IsValid())
	{
		TrackActor = Cast<ARaceTrackSpline>(UGameplayStatics::GetActorOfClass(GetWorld(), ARaceTrackSpline::StaticClass()));
	}

	USplineComponent* Spline = TrackActor.IsValid() ? TrackActor->GetSplineComponent() : nullptr;
	if (!Spline || Spline->GetSplineLength() < 100.0f)
	{
		return;
	}

	const float SplineLen = Spline->GetSplineLength();
	const FVector MyLoc = GetActorLocation();
	const float MyKey = Spline->FindInputKeyClosestToWorldLocation(MyLoc);
	const float MyDist = Spline->GetDistanceAlongSplineAtSplineInputKey(MyKey);

	int32 Rank = 1;
	float ClosestPoliceDist = 99999.0f;

	const float MyTotalDist = ((float)(CurrentLap - 1) * SplineLen) + DistanceAlongTrack;

	// Check all rival racers ahead of us on the circuit (accounting for completed laps)
	for (TActorIterator<AVrVehiclePawn> It(GetWorld()); It; ++It)
	{
		AVrVehiclePawn* OtherPawn = *It;
		if (OtherPawn && OtherPawn != this)
		{
			const float OtherTotalDist = ((float)(OtherPawn->CurrentLap - 1) * SplineLen) + OtherPawn->DistanceAlongTrack;
			if (OtherTotalDist > MyTotalDist)
			{
				Rank++;
			}
		}
	}

	// Check police cars for proximity alert
	for (TActorIterator<APoliceVehiclePawn> It(GetWorld()); It; ++It)
	{
		APoliceVehiclePawn* Police = *It;
		if (Police)
		{
			const float Dist3D = FVector::Dist(MyLoc, Police->GetActorLocation());
			if (Dist3D < ClosestPoliceDist)
			{
				ClosestPoliceDist = Dist3D;
			}
		}
	}

	CurrentRacePosition = FMath::Clamp(Rank, 1, 7);

	if (PositionTextRender)
	{
		if (bRaceFinished)
		{
			if (CurrentRacePosition == 1)
			{
				PositionTextRender->SetText(FText::FromString(TEXT("WINNER! P1")));
				PositionTextRender->SetTextRenderColor(FColor(255, 215, 0));
			}
			else
			{
				PositionTextRender->SetText(FText::FromString(FString::Printf(TEXT("FINAL: P%d"), CurrentRacePosition)));
				PositionTextRender->SetTextRenderColor(FColor(0, 255, 128));
			}
		}
		else
		{
			PositionTextRender->SetText(FText::FromString(FString::Printf(TEXT("P%d | LAP %d/%d"), CurrentRacePosition, CurrentLap, TotalLaps)));
			PositionTextRender->SetTextRenderColor(FColor(0, 245, 255));
		}
	}

	if (bRaceFinished && PoliceAlertTextRender)
	{
		if (CurrentRacePosition == 1)
		{
			PoliceAlertTextRender->SetText(FText::FromString(TEXT("★ VICTORY! YOU WIN! 1ST PLACE CHAMPION! ★  PRESS [R] TO RESTART")));
			PoliceAlertTextRender->SetTextRenderColor(FColor(255, 215, 0));
		}
		else
		{
			PoliceAlertTextRender->SetText(FText::FromString(FString::Printf(TEXT("CHECKERED FLAG! FINISHED P%d - PRESS [R] TO RESTART"), CurrentRacePosition)));
			PoliceAlertTextRender->SetTextRenderColor(FColor(0, 255, 128));
		}
		PoliceAlertTextRender->SetVisibility(true);
	}
	else if (PoliceAlertTextRender)
	{
		const float PoliceDistMeters = ClosestPoliceDist / 100.0f;
		if (PoliceDistMeters <= 40.0f)
		{
			PoliceAlertTextRender->SetText(FText::FromString(FString::Printf(TEXT("[!] POLICE INTERCEPTOR: %.0fm - USE NITRO!"), PoliceDistMeters)));
			PoliceAlertTextRender->SetTextRenderColor(FColor(255, 30, 30));
			PoliceAlertTextRender->SetVisibility(true);
		}
		else
		{
			// Agentic AI Copilot Tactical Navigation: Predicts upcoming track geometry
			float UpcomingCurveDeg = 0.0f;
			if (Spline)
			{
				const float LookaheadMeters = 85.0f;
				const FVector DirNow = Spline->GetDirectionAtDistanceAlongSpline(DistanceAlongTrack, ESplineCoordinateSpace::World);
				const FVector DirAhead = Spline->GetDirectionAtDistanceAlongSpline(DistanceAlongTrack + LookaheadMeters * 100.0f, ESplineCoordinateSpace::World);
				UpcomingCurveDeg = FMath::FindDeltaAngleDegrees(DirNow.Rotation().Yaw, DirAhead.Rotation().Yaw);
			}

			if (FMath::Abs(UpcomingCurveDeg) > 25.0f && GetSpeedKmh() > 85.0f)
			{
				if (UpcomingCurveDeg > 0.0f)
				{
					PoliceAlertTextRender->SetText(FText::FromString(TEXT("COPILOT: RIGHT TURN AHEAD! BRAKE")));
				}
				else
				{
					PoliceAlertTextRender->SetText(FText::FromString(TEXT("COPILOT: LEFT TURN AHEAD! BRAKE")));
				}
				PoliceAlertTextRender->SetTextRenderColor(FColor(255, 170, 0));
			}
			else if (CurrentRacePosition == 1)
			{
				PoliceAlertTextRender->SetText(FText::FromString(TEXT("COPILOT: POLE POSITION! MAINTAIN PACE")));
				PoliceAlertTextRender->SetTextRenderColor(FColor(255, 215, 0));
			}
			else
			{
				PoliceAlertTextRender->SetText(FText::FromString(TEXT("COPILOT: TRACK CLEAR - PUSH HARD")));
				PoliceAlertTextRender->SetTextRenderColor(FColor(0, 255, 128));
			}
			PoliceAlertTextRender->SetVisibility(true);
		}
	}

	// Update Rivian Central Screen AI Copilot Radar Status
	if (CentralScreenTacticalCopilot)
	{
		const float PoliceDistMeters = ClosestPoliceDist / 100.0f;
		if (PoliceDistMeters <= 50.0f)
		{
			CentralScreenTacticalCopilot->SetText(FText::FromString(FString::Printf(TEXT("TACTICAL ALERT: POLICE AT %.0fm (INTERCEPTOR)"), PoliceDistMeters)));
			CentralScreenTacticalCopilot->SetTextRenderColor(FColor(255, 40, 40));
		}
		else
		{
			CentralScreenTacticalCopilot->SetText(FText::FromString(FString::Printf(TEXT("AI COPILOT: SECTOR CLEAR | POS: P%d/7"), CurrentRacePosition)));
			CentralScreenTacticalCopilot->SetTextRenderColor(FColor(180, 235, 255));
		}
	}
}

void AVrVehiclePawn::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	if (!PlayerInputComponent)
	{
		return;
	}

	// 1. Standard Gamepad Analog Thumbsticks and Triggers
	if (EKeys::Gamepad_LeftX.IsAxis1D())
	{
		PlayerInputComponent->BindAxisKey(EKeys::Gamepad_LeftX, this, &AVrVehiclePawn::OnSteeringAngleUpdated);
	}
	if (EKeys::Gamepad_RightTriggerAxis.IsAxis1D())
	{
		PlayerInputComponent->BindAxisKey(EKeys::Gamepad_RightTriggerAxis, this, &AVrVehiclePawn::OnKeyThrottle);
	}
	if (EKeys::Gamepad_LeftTriggerAxis.IsAxis1D())
	{
		PlayerInputComponent->BindAxisKey(EKeys::Gamepad_LeftTriggerAxis, this, &AVrVehiclePawn::OnKeyBrake);
	}

	// 3. Oculus Touch Controller Bindings for VR (with IsAxis1D safety check)
	const FKey RightTrigger = EKeys::OculusTouch_Right_Trigger_Axis;
	const FKey LeftTrigger  = EKeys::OculusTouch_Left_Trigger_Axis;
	const FKey LeftStickX   = EKeys::OculusTouch_Left_Thumbstick_X;
	const FKey RightGrip    = EKeys::OculusTouch_Right_Grip_Axis;
	const FKey LeftGrip     = EKeys::OculusTouch_Left_Grip_Axis;

	if (RightTrigger.IsAxis1D())
	{
		PlayerInputComponent->BindAxisKey(RightTrigger, this, &AVrVehiclePawn::SetThrottle);
	}
	if (LeftTrigger.IsAxis1D())
	{
		PlayerInputComponent->BindAxisKey(LeftTrigger, this, &AVrVehiclePawn::SetBrake);
	}
	if (LeftStickX.IsAxis1D())
	{
		PlayerInputComponent->BindAxisKey(LeftStickX, this, &AVrVehiclePawn::OnSteeringAngleUpdated);
	}
	if (RightGrip.IsAxis1D())
	{
		PlayerInputComponent->BindAxisKey(RightGrip, this, &AVrVehiclePawn::HandleRightGrasp);
	}
	if (LeftGrip.IsAxis1D())
	{
		PlayerInputComponent->BindAxisKey(LeftGrip, this, &AVrVehiclePawn::HandleLeftGrasp);
	}

	// Press 'R' on keyboard or touch screen to restart race
	PlayerInputComponent->BindKey(EKeys::R, IE_Pressed, this, &AVrVehiclePawn::RestartRace);

	// Press 'M' on keyboard to toggle background music
	PlayerInputComponent->BindKey(EKeys::M, IE_Pressed, this, &AVrVehiclePawn::ToggleMusic);
}

void AVrVehiclePawn::OnKeyThrottle(float Val)
{
	if (Val > 0.05f)
	{
		SetThrottle(Val);
	}
}

void AVrVehiclePawn::OnKeyBrake(float Val)
{
	if (Val > 0.05f)
	{
		SetBrake(Val);
	}
}

void AVrVehiclePawn::OnKeySteerLeft(float Val)
{
	if (Val > 0.05f)
	{
		CurrentSteeringInput = -Val;
		if (ChaosMovementComp)
		{
			ChaosMovementComp->SetSteeringInput(-Val);
		}
	}
}

void AVrVehiclePawn::OnKeySteerRight(float Val)
{
	if (Val > 0.05f)
	{
		CurrentSteeringInput = Val;
		if (ChaosMovementComp)
		{
			ChaosMovementComp->SetSteeringInput(Val);
		}
	}
}

void AVrVehiclePawn::OnSteeringAngleUpdated(float NormalizedSteering)
{
	AxisSteerInput = NormalizedSteering;
	CurrentSteeringInput = NormalizedSteering;
	if (ChaosMovementComp)
	{
		ChaosMovementComp->SetSteeringInput(NormalizedSteering);
	}
}

void AVrVehiclePawn::HandleTacticalAdvice(const FCopilotTacticalOrder& Order)
{
	// Dispatches to Blueprint for 3D Widget display and Radio Audio playback
	OnCopilotOrderReceived(Order);
}

void AVrVehiclePawn::HandleLeftGrasp(float GraspStrength)
{
	if (SteeringWheelComponent && LeftHandMesh)
	{
		const bool bWasGrabbing = SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Left);
		if (SteeringWheelComponent->TryGrab(EVrHandSide::Left, LeftHandMesh, GraspStrength))
		{
			if (!bWasGrabbing)
			{
				TriggerHapticFeedback(0.3f, 0.08f, true, false);
			}
		}
		else
		{
			SteeringWheelComponent->TryRelease(EVrHandSide::Left, GraspStrength);
		}
	}
}

void AVrVehiclePawn::HandleRightGrasp(float GraspStrength)
{
	if (SteeringWheelComponent && RightHandMesh)
	{
		const bool bWasGrabbing = SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Right);
		if (SteeringWheelComponent->TryGrab(EVrHandSide::Right, RightHandMesh, GraspStrength))
		{
			if (!bWasGrabbing)
			{
				TriggerHapticFeedback(0.3f, 0.08f, false, true);
			}
		}
		else
		{
			SteeringWheelComponent->TryRelease(EVrHandSide::Right, GraspStrength);
		}
	}
}

void AVrVehiclePawn::HandleRightIndexCurl(float CurlStrength)
{
	// If right hand is gripping the wheel, index finger curl controls throttle
	if (SteeringWheelComponent && SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Right))
	{
		float ThrottleVal = (CurlStrength > FingerCurlDeadZone) 
			? (CurlStrength - FingerCurlDeadZone) / (1.0f - FingerCurlDeadZone) 
			: 0.0f;
		SetThrottle(ThrottleVal);
	}
	else
	{
		SetThrottle(0.0f);
	}
}

void AVrVehiclePawn::HandleLeftIndexCurl(float CurlStrength)
{
	// If left hand is gripping the wheel, index finger curl controls brake
	if (SteeringWheelComponent && SteeringWheelComponent->IsHandGrabbing(EVrHandSide::Left))
	{
		float BrakeVal = (CurlStrength > FingerCurlDeadZone) 
			? (CurlStrength - FingerCurlDeadZone) / (1.0f - FingerCurlDeadZone) 
			: 0.0f;
		SetBrake(BrakeVal);
	}
	else
	{
		SetBrake(0.0f);
	}
}

void AVrVehiclePawn::SetThrottle(float Value)
{
	CurrentRawThrottle = FMath::Clamp(Value, 0.0f, 1.0f);

	if (ChaosMovementComp)
	{
		float FinalThrottle = bIsNitroActive ? FMath::Clamp(CurrentRawThrottle * NitroBoostMultiplier, 0.0f, 1.0f) : CurrentRawThrottle;
		ChaosMovementComp->SetThrottleInput(FinalThrottle);
	}
}

void AVrVehiclePawn::SetBrake(float Value)
{
	if (ChaosMovementComp)
	{
		ChaosMovementComp->SetBrakeInput(FMath::Clamp(Value, 0.0f, 1.0f));
	}
}

void AVrVehiclePawn::SetHandbrake(bool bActive)
{
	if (ChaosMovementComp)
	{
		ChaosMovementComp->SetHandbrakeInput(bActive);
	}
}

void AVrVehiclePawn::ActivateNitro(bool bActive)
{
	if (bActive && NitroAmount > 5.0f)
	{
		bIsNitroActive = true;
		TriggerHapticFeedback(0.45f, 0.15f, true, true);
	}
	else
	{
		bIsNitroActive = false;
	}
}

void AVrVehiclePawn::ToggleEngine()
{
	bIsEngineStarted = !bIsEngineStarted;
	if (EngineAudioComponent)
	{
		if (bIsEngineStarted)
		{
			EngineAudioComponent->Play();
		}
		else
		{
			EngineAudioComponent->Stop();
			FallbackSpeedKmh = 0.0f;
		}
	}
}

float AVrVehiclePawn::GetSpeedKmh() const
{
	if (GetMesh() && GetMesh()->IsSimulatingPhysics() && ChaosMovementComp)
	{
		const float ChaosSpeed = FMath::Abs(ChaosMovementComp->GetForwardSpeed()) * 0.036f;
		if (ChaosSpeed > 0.5f)
		{
			return ChaosSpeed;
		}
	}

	if (FMath::Abs(FallbackSpeedKmh) > 0.1f)
	{
		return FMath::Abs(FallbackSpeedKmh);
	}

	return GetVelocity().Size() * 0.036f;
}

void AVrVehiclePawn::RestartRace()
{
	RaceCountdownTimer = 3.99f;
	bIsRaceActive = false;
	bRaceFinished = false;
	CurrentLap = 1;
	TotalLaps = 5;
	PreviousDistanceAlongTrack = 1200.0f;
	LateralBounceVelocity = 0.0f;
	DistanceAlongTrack = 1200.0f;
	LateralTrackOffset = -160.0f;
	FallbackSpeedKmh = 0.0f;
	CurrentSteeringInput = 0.0f;
	NitroAmount = 100.0f;
	bIsNitroActive = false;
	bIsBusted = false;
	BustedTimer = 0.0f;

	// Reset Rivals to starting grid with competitive launch spacing & speeds
	int32 RivalIdx = 0;
	const float RivalDists[5] = { 4600.0f, 3500.0f, 2500.0f, 1900.0f, 1500.0f };
	const float RivalOffsets[5] = { 160.0f, -160.0f, 160.0f, -160.0f, 160.0f };
	const float RivalSpeeds[5] = { 210.0f, 200.0f, 190.0f, 180.0f, 170.0f };
	for (TActorIterator<AVrVehiclePawn> It(GetWorld()); It; ++It)
	{
		AVrVehiclePawn* Pawn = *It;
		if (Pawn && Pawn != this && Pawn->bIsAiRacer)
		{
			Pawn->CurrentLap = 1;
			Pawn->bRaceFinished = false;
			Pawn->PreviousDistanceAlongTrack = 1200.0f;
			if (RivalIdx < 5)
			{
				Pawn->DistanceAlongTrack = RivalDists[RivalIdx];
				Pawn->LateralTrackOffset = RivalOffsets[RivalIdx];
				Pawn->FallbackSpeedKmh = RivalSpeeds[RivalIdx];
				RivalIdx++;
			}
		}
	}

	// Reset Police to parked ambush spots along the road
	int32 PoliceIdx = 0;
	const float PoliceDists[3] = { 18000.0f, 38000.0f, 62000.0f };
	const float PoliceOffsets[3] = { 540.0f, -540.0f, 540.0f };
	for (TActorIterator<APoliceVehiclePawn> It(GetWorld()); It; ++It)
	{
		APoliceVehiclePawn* PolicePawn = *It;
		if (PolicePawn)
		{
			if (PoliceIdx < 3)
			{
				PolicePawn->ResetAmbush(PoliceDists[PoliceIdx], PoliceOffsets[PoliceIdx]);
				PoliceIdx++;
			}
		}
	}

	if (PoliceAlertTextRender)
	{
		PoliceAlertTextRender->SetText(FText::FromString(TEXT("RACE RESTARTED - FULL THROTTLE!")));
		PoliceAlertTextRender->SetTextRenderColor(FColor(0, 245, 255));
	}

	// Ensure background music is playing for local player
	if (!bIsAiRacer && MusicAudioComponent && !MusicAudioComponent->IsPlaying())
	{
		MusicAudioComponent->Play();
	}
}

void AVrVehiclePawn::ToggleMusic()
{
	if (!MusicAudioComponent) return;

	if (MusicAudioComponent->IsPlaying())
	{
		MusicAudioComponent->Stop();
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(88, 2.5f, FColor(255, 128, 0), TEXT(">>> MUSIC: [MUTED] (M) <<<"), true, FVector2D(1.3f, 1.3f));
		}
	}
	else
	{
		MusicAudioComponent->Play();
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(88, 2.5f, FColor(0, 255, 128), TEXT(">>> MUSIC: [PLAYING] (M) <<<"), true, FVector2D(1.3f, 1.3f));
		}
	}
}

void AVrVehiclePawn::TriggerHapticFeedback(float Intensity, float Duration, bool bLeftHand, bool bRightHand)
{
	APlayerController* PC = Cast<APlayerController>(GetController());
	if (PC && PC->IsLocalController())
	{
		PC->PlayDynamicForceFeedback(Intensity, Duration, bLeftHand, bLeftHand, bRightHand, bRightHand);
	}
}

