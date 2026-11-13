// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "WheeledVehiclePawn.h"
#include "PoliceVehiclePawn.generated.h"

class UPointLightComponent;
class URaceTrackFollowerComponent;
class UChaosWheeledVehicleMovementComponent;
class UAudioComponent;
class AVrVehiclePawn;

/**
 * AI Police Pursuit Vehicle Pawn.
 * Features aggressive player pursuit, flashing red/blue siren lights,
 * track-following fallback via spline, and real-time copilot proximity dispatch.
 */
UCLASS()
class VRMPC_API APoliceVehiclePawn : public AWheeledVehiclePawn
{
	GENERATED_BODY()

public:
	APoliceVehiclePawn();

	virtual void Tick(float DeltaTime) override;
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	/** Toggles police siren flashing and siren lights */
	UFUNCTION(BlueprintCallable, Category = "Police|Siren")
	void SetSirenActive(bool bActive);

	/** Manually sets the player target vehicle */
	UFUNCTION(BlueprintCallable, Category = "Police|AI")
	void SetTargetPlayer(AVrVehiclePawn* PlayerPawn);

	/** Returns current speed in km/h */
	UFUNCTION(BlueprintPure, Category = "Police|Physics")
	float GetSpeedKmh() const;

	/** Accessor for Spline Follower Component */
	UFUNCTION(BlueprintPure, Category = "Police|AI")
	URaceTrackFollowerComponent* GetSplineFollower() const { return SplineFollower; }

	UFUNCTION(BlueprintPure, Category = "Police|Track")
	float GetDistanceAlongTrack() const { return DistanceAlongTrack; }

	UFUNCTION(BlueprintPure, Category = "Police|Track")
	float GetLateralTrackOffset() const { return LateralTrackOffset; }

	/** Whether this interceptor starts parked on the shoulder waiting to ambush the player */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Police|Ambush")
	bool bIsParkedAmbush = true;

	/** Distance threshold to spring the ambush when player speeds past (cm) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Police|Ambush")
	float AmbushTriggerDistance = 3500.0f;

	/** Reset police state back to parked ambush */
	UFUNCTION(BlueprintCallable, Category = "Police|Ambush")
	void ResetAmbush(float InDistanceAlongTrack, float InLateralOffset);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Police|Track")
	float DistanceAlongTrack = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Police|Track")
	float LateralTrackOffset = 0.0f;

	/** Flashing frequency in Hertz */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Police|Siren")
	float SirenStrobeRate = 6.0f;

	/** Proximity distance in cm to trigger Copilot radio warning (1500 cm = 15m) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Police|AI")
	float ProximityAlertDistance = 1500.0f;

	/** Maximum pursuit speed in km/h */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Police|AI")
	float MaxPursuitSpeedKmh = 175.0f;

	/** Steering response gain during pursuit */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Police|AI")
	float PursuitSteeringGain = 2.4f;

	/** Cooldown between radio warning dispatches in seconds */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Police|AI")
	float AlertCooldownSeconds = 6.0f;

protected:
	virtual void BeginPlay() override;

	/** Visual Static Mesh for the Police Vehicle Chassis */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Police|Mesh")
	TObjectPtr<UStaticMeshComponent> ChassisMeshComponent;

	/** Red Siren Point Light on car roof */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Police|Siren")
	TObjectPtr<UPointLightComponent> RedSirenLight;

	/** Blue Siren Point Light on car roof */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Police|Siren")
	TObjectPtr<UPointLightComponent> BlueSirenLight;

	/** Red Siren Visual Mesh on car roof */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Police|Siren")
	TObjectPtr<UStaticMeshComponent> RedSirenMesh;

	/** Blue Siren Visual Mesh on car roof */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Police|Siren")
	TObjectPtr<UStaticMeshComponent> BlueSirenMesh;

	/** Spline Follower for track navigation */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Police|AI")
	TObjectPtr<URaceTrackFollowerComponent> SplineFollower;

	/** Engine Audio Component */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Police|Audio")
	TObjectPtr<UAudioComponent> EngineAudioComponent;

	/** Police Siren Audio Component */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Police|Audio")
	TObjectPtr<UAudioComponent> SirenAudioComponent;

private:
	UPROPERTY()
	TObjectPtr<UChaosWheeledVehicleMovementComponent> ChaosMovementComp;

	UPROPERTY()
	TWeakObjectPtr<AVrVehiclePawn> TargetPlayerPawn;

	UPROPERTY()
	TWeakObjectPtr<class ARaceTrackSpline> TrackActor;

	bool bIsSirenActive = true;
	float StrobeTimer = 0.0f;
	float TimeSinceLastAlert = 100.0f;
	float FallbackPoliceSpeedKmh = 0.0f;

	void UpdateSirenLights(float DeltaTime);
	void UpdatePursuitAI(float DeltaTime);
	void CheckProximityAndAlertPlayer();
	void FindPlayerPawn();
};

