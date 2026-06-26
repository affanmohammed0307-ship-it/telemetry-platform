def check_alert(sensor_id, value):
    
    if sensor_id == "engine_temp":
        if value > 115:
            return "🔴 CRITICAL: Engine overheating. Possible causes: coolant leak, thermostat failure, blocked radiator. Immediate inspection required."
        elif value > 105:
            return "🟠 WARNING: Engine temperature high. Monitor closely — may indicate cooling system stress."
        elif value < 85:
            return "🔵 INFO: Engine running cold. Possible causes: thermostat stuck open, short trip cycle."
    
    if sensor_id == "battery_voltage":
        if value < 11.8:
            return "🔴 CRITICAL: Battery voltage critically low. Possible causes: alternator failure, parasitic drain, aging battery."
        elif value < 12.2:
            return "🟠 WARNING: Battery voltage below optimal. Check charging system."
        elif value > 14.8:
            return "🔴 CRITICAL: Battery overcharging detected. Possible causes: faulty voltage regulator."
    
    return None