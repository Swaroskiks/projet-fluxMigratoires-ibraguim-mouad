import pandas as pd
from src.components import haversine_distance

def calculate_speed(row1, row2):
    """Calcule la vitesse entre deux points."""
    distance = haversine_distance(
        row1['location_lat'], row1['location_long'],
        row2['location_lat'], row2['location_long']
    )
    time_diff = (row2['timestamp'] - row1['timestamp']).total_seconds() / 3600  # en heures
    return distance / time_diff if time_diff > 0 else 0

def compute_speeds(group):
    """Calcule les vitesses pour un groupe de points."""
    speeds = [0]
    for i in range(1, len(group)):
        speed = calculate_speed(group.iloc[i-1], group.iloc[i])
        speeds.append(speed)
    group['speed'] = speeds
    return group

def calculate_active_distance(group):
    """Calcule la distance totale pendant la migration active."""
    total_distance = 0
    for i in range(len(group) - 1):
        lat1, lon1 = group.iloc[i]['location_lat'], group.iloc[i]['location_long']
        lat2, lon2 = group.iloc[i + 1]['location_lat'], group.iloc[i + 1]['location_long']
        total_distance += haversine_distance(lat1, lon1, lat2, lon2)
    return total_distance

def calculate_active_duration(group):
    """Calcule la durée de la migration active."""
    if len(group) > 1:
        return (group['timestamp'].max() - group['timestamp'].min()).days
    return 0

def calculate_migration_stats(df):
    """Calcule les statistiques de migration (distance moyenne et durée)."""
    # Nettoyage et tri des données
    df = df.copy()
    df = df[(df['location_lat'].between(-90, 90)) & (df['location_long'].between(-180, 180))]
    df = df.sort_values(['individual_id', 'timestamp'])
    
    # Calcul des vitesses
    df = df.groupby('individual_id', group_keys=False).apply(compute_speeds)
    
    # Filtrage des points de migration active
    SPEED_THRESHOLD = 20
    active_migration = df[df['speed'] >= SPEED_THRESHOLD].copy()
    active_migration['year'] = active_migration['timestamp'].dt.year
    
    # Calcul des distances et durées par individu et année
    distances = []
    durations = []
    
    for (ind, year), group in active_migration.groupby(['individual_id', 'year']):
        distance = calculate_active_distance(group)
        duration = calculate_active_duration(group)
        
        if distance > 0 and duration > 0:
            distances.append(distance)
            durations.append(duration)
    
    # Calcul des moyennes
    avg_distance = int(sum(distances) / len(distances)) if distances else 0
    avg_duration = int(sum(durations) / len(durations)) if durations else 0
    
    return avg_distance, avg_duration

def calculate_total_distance(df):
    """Calcule la distance totale parcourue."""
    total_distance = 0
    for individual in df['individual_id'].unique():
        ind_data = df[df['individual_id'] == individual].sort_values('timestamp')
        for i in range(len(ind_data) - 1):
            lat1, lon1 = ind_data.iloc[i]['location_lat'], ind_data.iloc[i]['location_long']
            lat2, lon2 = ind_data.iloc[i + 1]['location_lat'], ind_data.iloc[i + 1]['location_long']
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            if distance <= 300:  # Filtre des distances aberrantes
                total_distance += distance
    return total_distance

def calculate_average_speed(df):
    """Calcule la vitesse moyenne."""
    total_speed = 0
    speed_count = 0
    for individual in df['individual_id'].unique():
        ind_data = df[df['individual_id'] == individual].sort_values('timestamp')
        for i in range(len(ind_data) - 1):
            lat1, lon1 = ind_data.iloc[i]['location_lat'], ind_data.iloc[i]['location_long']
            lat2, lon2 = ind_data.iloc[i + 1]['location_lat'], ind_data.iloc[i + 1]['location_long']
            time1, time2 = ind_data.iloc[i]['timestamp'], ind_data.iloc[i + 1]['timestamp']
            
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            time_diff = (time2 - time1).total_seconds() / 3600
            
            if distance <= 300 and time_diff > 0:
                speed = distance / time_diff
                if speed >= 20:  # Seuil de vitesse pour la migration active
                    total_speed += speed
                    speed_count += 1
    
    return int(total_speed / speed_count) if speed_count > 0 else 0

def calculate_max_amplitude(df):
    """Calcule l'amplitude maximale des déplacements."""
    points = [
        (df.loc[df['location_lat'].idxmin(), ['location_lat', 'location_long']]),
        (df.loc[df['location_lat'].idxmax(), ['location_lat', 'location_long']]),
        (df.loc[df['location_long'].idxmin(), ['location_lat', 'location_long']]),
        (df.loc[df['location_long'].idxmax(), ['location_lat', 'location_long']])
    ]
    
    max_distance = 0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            lat1, lon1 = points[i]
            lat2, lon2 = points[j]
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            max_distance = max(max_distance, distance)
    
    return int(max_distance)

def calculate_monthly_distances(df):
    """Calcule les distances mensuelles."""
    df = df.sort_values(['individual_id', 'timestamp'])
    df['month'] = df['timestamp'].dt.to_period('M')
    
    monthly_distances = []
    for individual in df['individual_id'].unique():
        ind_data = df[df['individual_id'] == individual]
        for month in ind_data['month'].unique():
            month_data = ind_data[ind_data['month'] == month].copy()
            if len(month_data) < 2:
                continue
            
            total_distance = 0
            for i in range(len(month_data) - 1):
                lat1, lon1 = month_data.iloc[i]['location_lat'], month_data.iloc[i]['location_long']
                lat2, lon2 = month_data.iloc[i + 1]['location_lat'], month_data.iloc[i + 1]['location_long']
                distance = haversine_distance(lat1, lon1, lat2, lon2)
                if distance <= 300:
                    total_distance += distance
            
            if total_distance > 0:
                monthly_distances.append({
                    'individual': individual,
                    'month': month,
                    'distance': total_distance
                })
    
    if not monthly_distances:
        return pd.DataFrame(columns=['month', 'avg_distance', 'min_distance', 'max_distance'])
    
    monthly_stats = pd.DataFrame(monthly_distances)
    monthly_summary = monthly_stats.groupby('month').agg({
        'distance': ['mean', 'min', 'max']
    }).reset_index()
    
    monthly_summary.columns = ['month', 'avg_distance', 'min_distance', 'max_distance']
    return monthly_summary