from profile_generator.combine_profiles import main


scenarios = 1000

for s in range(1, scenarios + 1):

    main(scenario_name=f"scenario_{s}")
    
    break