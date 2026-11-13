// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Interfaces/IHttpRequest.h"
#include "CarAIAgentComponent.generated.h"

class AVrVehiclePawn;

/** Telemetry packet sent to AI backend */
USTRUCT(BlueprintType)
struct FVehicleTelemetryData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Telemetry")
	float SpeedKmh = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Telemetry")
	float DistanceToRivalAhead = -1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Telemetry")
	float DistanceToRivalBehind = -1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Telemetry")
	float NitroPercentage = 100.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Telemetry")
	int32 CurrentGear = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Telemetry")
	FString TrackSector = TEXT("Sector_1");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Telemetry")
	float LateralGForce = 0.0f;
};

/** Tactical order / advice received from AI Copilot backend */
USTRUCT(BlueprintType)
struct FCopilotTacticalOrder
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Copilot")
	FString AdviceMessage;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Copilot")
	FString TacticalAction; // e.g. "USE_NITRO", "DEFEND_LEFT", "DRIFT_ENTRY", "OVERTAKE_RIGHT"

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Copilot")
	float SuggestedSpeed = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Copilot")
	FString CopilotMood; // e.g. "CALM", "URGENT", "AGGRESSIVE"

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Copilot")
	int32 VoiceCueId = 0;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTacticalAdviceReceived, const FCopilotTacticalOrder&, TacticalOrder);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnCopilotHttpError, int32, StatusCode, const FString&, ErrorMessage);

/**
 * Lightweight C++ Actor Component managing asynchronous HTTP communication
 * with tactical AI copilot and pursuit AI backend without blocking the Game Thread.
 */
UCLASS(ClassGroup=(AI), meta=(BlueprintSpawnableComponent))
class VRMPC_API UCarAIAgentComponent : public UActorComponent
{
	GENERATED_BODY()

public:	
	UCarAIAgentComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/** Sends telemetry payload to backend asynchronously */
	UFUNCTION(BlueprintCallable, Category = "AI|Copilot")
	void SendTelemetry(const FVehicleTelemetryData& Telemetry);

	/** Sends an immediate event alert (e.g. "RIVAL_OVERTAKE", "CRASH_IMMINENT") bypassing interval */
	UFUNCTION(BlueprintCallable, Category = "AI|Copilot")
	void SendImmediateEventAlert(const FString& EventType, const FString& EventDetails);

	/** Broadcasts when copilot order is received and parsed */
	UPROPERTY(BlueprintAssignable, Category = "AI|Copilot")
	FOnTacticalAdviceReceived OnTacticalAdviceReceived;

	/** Broadcasts when network request encounters an error */
	UPROPERTY(BlueprintAssignable, Category = "AI|Copilot")
	FOnCopilotHttpError OnCopilotHttpError;

	/** Backend URL for AI Copilot tactics endpoint */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Copilot")
	FString BackendEndpointUrl = TEXT("https://ai-backend.tu-dominio.com/api/v1/copilot/tactics");

	/** Telemetry dispatch interval in seconds */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Copilot")
	float TelemetryIntervalSeconds = 2.0f;

	/** Automatically gather telemetry from owning AVrVehiclePawn (disabled by default until backend is running) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI|Copilot")
	bool bAutoGatherVehicleTelemetry = false;

protected:
	virtual void BeginPlay() override;

private:
	float TimeSinceLastTelemetry = 0.0f;
	bool bIsRequestInFlight = false;

	UPROPERTY()
	TWeakObjectPtr<AVrVehiclePawn> CachedVehiclePawn;

	void HandleHttpResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bConnectedSuccessfully);
	FVehicleTelemetryData GatherCurrentTelemetry() const;
};

