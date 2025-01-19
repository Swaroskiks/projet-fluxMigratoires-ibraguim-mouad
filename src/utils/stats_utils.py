"""Migration statistics utilities.

Provides functions to calculate various migration statistics, including:
- **Temporal statistics:** migration duration, regional time distribution, active periods.
- **Spatial statistics:** total and average distances, migration amplitude.
- **Speed statistics:** average and seasonal speeds, peak velocities.
"""

from typing import List, Tuple
import pandas as pd
from src.components import haversine_distance

def calculate_speed(row1: pd.Series, row2: pd.Series) -> float:
    """Calculate speed between two points.
    
    Args:
        row1 (pd.Series): First point.
        row2 (pd.Series): Second point.
        
    Returns:
        float: Speed between the two points.
    """
    distance = haversine_distance(
        row1['location_lat'], row1['location_long'],
        row2['location_lat'], row2['location_long']
    )
    time_diff = (row2['timestamp'] - row1['timestamp']).total_seconds() / 3600  # en heures
    return distance / time_diff if time_diff > 0 else 0

def compute_speeds(group: pd.DataFrame) -> pd.DataFrame:
    """Compute speed for each movement within a group of points.
    
    Args:
        group (pd.DataFrame): Group of points.
    
    Returns:
        pd.DataFrame: DataFrame with speed column.
    """
    speeds: List[float] = [0.0]
    for i in range(1, len(group)):
        speed = calculate_speed(group.iloc[i-1], group.iloc[i])
        speeds.append(speed)
    group['speed'] = speeds
    return group

def calculate_active_distance(group: pd.DataFrame) -> float:
    """Calculate total distance during active migration.
    
    Args:
        group (pd.DataFrame): Group of points.
    
    Returns:
        float: Total distance during active migration.
    """
    total_distance: float = 0.0
    for i in range(len(group) - 1):
        lat1, lon1 = group.iloc[i]['location_lat'], group.iloc[i]['location_long']
        lat2, lon2 = group.iloc[i + 1]['location_lat'], group.iloc[i + 1]['location_long']
        total_distance += haversine_distance(lat1, lon1, lat2, lon2)
    return total_distance

def calculate_active_duration(group: pd.DataFrame) -> int:
    """Calculate the duration of active migration.
    
    Args:
        group (pd.DataFrame): Group of points.
    
    Returns:
        int: Duration of active migration in days.
    """
    if len(group) > 1:
        return (group['timestamp'].max() - group['timestamp'].min()).days
    return 0

def calculate_migration_stats(df: pd.DataFrame) -> Tuple[int, int]:
    """Calculate migration statistics: average distance and duration.
    
    Args:
        df (pd.DataFrame): DataFrame with location data.
    
    Returns:
        Tuple[int, int]: Average distance and duration.
    """
    # Data cleaning and filtering
    df = df.copy()
    df = df[(df['location_lat'].between(-90, 90)) & (df['location_long'].between(-180, 180))]
    df = df.sort_values(['individual_id', 'timestamp'])
    
    # Speed calculation
    df = df.groupby('individual_id', group_keys=False).apply(compute_speeds)
    
    # Filtering active migration points
    SPEED_THRESHOLD = 20
    active_migration = df[df['speed'] >= SPEED_THRESHOLD].copy()
    active_migration['year'] = active_migration['timestamp'].dt.year
    
    # Calculation of distances and durations per individual and year
    distances = []
    durations = []
    
    for (ind, year), group in active_migration.groupby(['individual_id', 'year']):
        distance = calculate_active_distance(group)
        duration = calculate_active_duration(group)
        
        if distance > 0 and duration > 0:
            distances.append(distance)
            durations.append(duration)
    
    # Calculation of averages
    avg_distance = int(sum(distances) / len(distances)) if distances else 0
    avg_duration = int(sum(durations) / len(durations)) if durations else 0
    
    return avg_distance, avg_duration

def calculate_total_distance(df: pd.DataFrame) -> float:
    """Calculate the total distance traveled.
    
    Args:
        df (pd.DataFrame): DataFrame with location data.
    
    Returns:
        float: Total distance traveled.
    """
    total_distance: float = 0.0
    for individual in df['individual_id'].unique():
        ind_data = df[df['individual_id'] == individual].sort_values('timestamp')
        for i in range(len(ind_data) - 1):
            lat1, lon1 = ind_data.iloc[i]['location_lat'], ind_data.iloc[i]['location_long']
            lat2, lon2 = ind_data.iloc[i + 1]['location_lat'], ind_data.iloc[i + 1]['location_long']
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            if distance <= 300:  # Filtering out anomalous distances
                total_distance += distance
    return total_distance
int
def calculate_average_speed(df: pd.DataFrame) -> int:
    """Calculate the average migration speed.
    
    Args:
        df (pd.DataFrame): DataFrame with location data.
    
    Returns:
        int: Average migration speed.
    """
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

def calculate_max_amplitude(df: pd.DataFrame) -> int:
    """Calculate the maximum migration amplitude.
    
    Args:
        df (pd.DataFrame): DataFrame with location data.
    
    Returns:
        int: Maximum migration amplitude.
    """
    points = [
        (df.loc[df['location_lat'].idxmin(), ['location_lat', 'location_long']]),
        (df.loc[df['location_lat'].idxmax(), ['location_lat', 'location_long']]),
        (df.loc[df['location_long'].idxmin(), ['location_lat', 'location_long']]),
        (df.loc[df['location_long'].idxmax(), ['location_lat', 'location_long']])
    ]
    
    max_distance: float = 0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            lat1, lon1 = points[i]
            lat2, lon2 = points[j]
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            max_distance = max(max_distance, distance)
    
    return int(max_distance)

def calculate_monthly_distances(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly migration distances.
    
    Args:
        df (pd.DataFrame): DataFrame with location data.
    
    Returns:
        pd.DataFrame: DataFrame with monthly migration distances.
    """
    if df.empty:
        return pd.DataFrame(columns=['individual', 'month', 'distance'])

    df = df.sort_values(['individual_id', 'timestamp'])
    df['month'] = df['timestamp'].dt.to_period('M')
    
    monthly_distances = []
    for individual in df['individual_id'].unique():
        ind_data = df[df['individual_id'] == individual]
        for month in ind_data['month'].unique():
            month_data = ind_data[ind_data['month'] == month].copy()
            if len(month_data) < 2:
                continue
            
            total_distance: float = 0.0
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