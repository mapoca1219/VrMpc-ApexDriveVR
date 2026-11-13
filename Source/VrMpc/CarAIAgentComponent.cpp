// Fill out your copyright notice in the Description page of Project Settings.

#include "CarAIAgentComponent.h"
#include "VrVehiclePawn.h"
#include "HttpModule.h"
#include "Interfaces/IHttpResponse.h"
#include "JsonObjectConverter.h"

UCarAIAgentComponent::UCarAIAgentComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UCarAIAgentComponent::BeginPlay()
{
	Super::BeginPlay();
	CachedVehiclePawn = Cast<AVrVehiclePawn>(GetOwner());
}

void UCarAIAgentComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	TimeSinceLastTelemetry += DeltaTime;
	if (bAutoGatherVehicleTelemetry && TimeSinceLastTelemetry >= TelemetryIntervalSeconds)
	{
		TimeSinceLastTelemetry = 0.0f;

		// Only dispatch periodic telemetry if previous request has resolved
		if (!bIsRequestInFlight)
		{
			SendTelemetry(GatherCurrentTelemetry());
		}
	}
}

FVehicleTelemetryData UCarAIAgentComponent::GatherCurrentTelemetry() const
{
	FVehicleTelemetryData Data;

	if (CachedVehiclePawn.IsValid())
	{
		Data.SpeedKmh = CachedVehiclePawn->GetSpeedKmh();
		Data.NitroPercentage = CachedVehiclePawn->GetNitroPercentage();
		Data.TrackSector = TEXT("Track_MainSector");

		// Compute lateral acceleration / G-Force approximation
		FVector LocalVelocity = CachedVehiclePawn->GetActorTransform().InverseTransformVector(CachedVehiclePawn->GetVelocity());
		Data.LateralGForce = (LocalVelocity.Y / 100.0f) / 9.8f;
	}

	return Data;
}

void UCarAIAgentComponent::SendTelemetry(const FVehicleTelemetryData& Telemetry)
{
	FString JsonPayload;
	if (!FJsonObjectConverter::UStructToJsonObjectString(Telemetry, JsonPayload))
	{
		UE_LOG(LogTemp, Error, TEXT("[CarAI] Failed to serialize telemetry struct to JSON"));
		return;
	}

	TSharedRef<IHttpRequest, ESPMode::ThreadSafe> HttpRequest = FHttpModule::Get().CreateRequest();
	HttpRequest->OnProcessRequestComplete().BindUObject(this, &UCarAIAgentComponent::HandleHttpResponse);
	HttpRequest->SetURL(BackendEndpointUrl);
	HttpRequest->SetVerb(TEXT("POST"));
	HttpRequest->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
	HttpRequest->SetHeader(TEXT("Accept"), TEXT("application/json"));
	HttpRequest->SetContentAsString(JsonPayload);
	HttpRequest->SetTimeout(2.5f); // 2.5 second timeout to keep responses fresh

	bIsRequestInFlight = true;
	HttpRequest->ProcessRequest();
}

void UCarAIAgentComponent::SendImmediateEventAlert(const FString& EventType, const FString& EventDetails)
{
	TSharedPtr<FJsonObject> JsonObj = MakeShared<FJsonObject>();
	JsonObj->SetStringField(TEXT("EventType"), EventType);
	JsonObj->SetStringField(TEXT("EventDetails"), EventDetails);
	JsonObj->SetNumberField(TEXT("SpeedKmh"), CachedVehiclePawn.IsValid() ? CachedVehiclePawn->GetSpeedKmh() : 0.0f);

	FString JsonPayload;
	TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonPayload);
	FJsonSerializer::Serialize(JsonObj.ToSharedRef(), Writer);

	TSharedRef<IHttpRequest, ESPMode::ThreadSafe> HttpRequest = FHttpModule::Get().CreateRequest();
	HttpRequest->OnProcessRequestComplete().BindUObject(this, &UCarAIAgentComponent::HandleHttpResponse);
	HttpRequest->SetURL(BackendEndpointUrl + TEXT("/alert"));
	HttpRequest->SetVerb(TEXT("POST"));
	HttpRequest->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
	HttpRequest->SetContentAsString(JsonPayload);
	HttpRequest->SetTimeout(1.5f);
	HttpRequest->ProcessRequest();
}

void UCarAIAgentComponent::HandleHttpResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bConnectedSuccessfully)
{
	bIsRequestInFlight = false;

	if (!bConnectedSuccessfully || !Response.IsValid())
	{
		// Back off periodic telemetry when backend is offline
		TimeSinceLastTelemetry = -8.0f; 
		OnCopilotHttpError.Broadcast(0, TEXT("Offline mode"));
		return;
	}

	const int32 ResponseCode = Response->GetResponseCode();
	if (ResponseCode != 200)
	{
		UE_LOG(LogTemp, Warning, TEXT("[CarAI] HTTP Request returned status %d"), ResponseCode);
		OnCopilotHttpError.Broadcast(ResponseCode, Response->GetContentAsString());
		return;
	}

	const FString ResponseString = Response->GetContentAsString();
	FCopilotTacticalOrder TacticalOrder;

	if (FJsonObjectConverter::JsonObjectStringToUStruct(ResponseString, &TacticalOrder, 0, 0))
	{
		OnTacticalAdviceReceived.Broadcast(TacticalOrder);
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("[CarAI] Failed to deserialize tactical order JSON: %s"), *ResponseString);
	}
}

