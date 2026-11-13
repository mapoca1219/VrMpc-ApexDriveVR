// Fill out your copyright notice in the Description page of Project Settings.

using UnrealBuildTool;

public class VrMpc : ModuleRules
{
	public VrMpc(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
	
		PublicDependencyModuleNames.AddRange(new string[] { 
			"Core", 
			"CoreUObject", 
			"Engine", 
			"InputCore",
			"EnhancedInput",
			"ChaosVehicles",
			"HeadMountedDisplay",
			"XRBase",
			"HTTP",
			"Json",
			"JsonUtilities",
			"UMG",
			"AIModule"
		});

		PrivateDependencyModuleNames.AddRange(new string[] {  });
	}
}
