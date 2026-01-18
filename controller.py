"""Controller model."""


def controller_function(
    power_set_point_hp: float, voltage: float, temperature: float, controller_settings: dict,
) -> float:
    """A simple controller for co-simulated coupled electric grid, heat pump, and building systems.
    
    The controller is used to adjust the power setpoint of the heat pump based boundary conditions.
    """
    # Boundary conditions
    voltage_min = controller_settings['ControllerSettings']['boundary_conditions']['minimum_voltage']
    voltage_max = controller_settings['ControllerSettings']['boundary_conditions']['maximum_voltage']
    temp_min = controller_settings['ControllerSettings']['boundary_conditions']['minimum_temperature']
    temp_max = controller_settings['ControllerSettings']['boundary_conditions']['maximum_temperature']
    
    p_adjust_step_size_voltage = controller_settings['ControllerSettings']['actions']['p_change_for_voltage']
    p_adjust_step_size_temp = controller_settings['ControllerSettings']['actions']['p_change_for_temperature']

    # Log current state of the system
    print(f"Current power setpoint of the heat pump: {power_set_point_hp}")
    print(f"Current grid voltage: {voltage}")
    print(f"Current temperature: {temperature}")

    # Temperature control: Turn on or off the heat pump based on temperature needs (when the voltage is within limits)
    if voltage_min <= voltage <= voltage_max:
        if temperature > temp_max:
            power_set_point_hp = 0
            print("Temperature is too high, turn off the heat pump to cool down.")
        elif temperature < temp_min:
            power_set_point_hp = p_adjust_step_size_temp
            print("Temperature is too low, turn on the heat pump to warm up.")

    # Voltage control: Turn on or off the heat pump based on voltage limits (Voltage control has higher priority when the temperature is low)
    elif voltage < voltage_min:
        power_set_point_hp = 0
        print(f"Voltage {voltage} too low, turn off the heat pump to correct voltage.")
    elif voltage > voltage_max:
        if temperature < temp_max:
            power_set_point_hp = p_adjust_step_size_voltage
            print(f"Voltage {voltage} too high, turn on the heat pump to correct voltage.")
        else:
            power_set_point_hp = 0
            print(f"Although the voltage {voltage} too high and we need to turn on the heat pump, but temperature {temperature} is too high, the heat pump has to be turned off.")
    else:
        print()

    return power_set_point_hp