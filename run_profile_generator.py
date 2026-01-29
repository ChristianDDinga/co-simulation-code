from profile_generator.combine_profiles import main

if __name__ == "__main__":

    scenarios = 1000

    for s in range(1, scenarios + 1):

        main(scenario_name=f"scenario_{s}")
        
        break