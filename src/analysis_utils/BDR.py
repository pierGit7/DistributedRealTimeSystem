from common.SRPModel import SRPModel

def get_availability_factor(model: SRPModel):
    """
    Calculate the availability factor for a given SRP model.
    
    Args:
        model (SRPModel): The SRP model to calculate the availability factor for.
        
    Returns:
        float: The availability factor for the given SRP model.
    """
    # Calculate the total time period
    total_time_period = model.period
    
    # Calculate the total resource access time
    total_resource_access_time = sum(end - start for start, end in model.resource_access)
    
    # Calculate the availability factor
    availability_factor = total_resource_access_time / total_time_period
    
    return availability_factor

def get_partion_delay(model: SRPModel):
    """
    Calculate the partition delay for a given SRP model.
    
    Args:
        model (SRPModel): The SRP model to calculate the partition delay for.
        
    Returns:
        float: The partition delay for the given SRP model.
    """
    # Calculate the total time period
    total_time_period = model.period
    
    # Calculate the total resource access time
    total_resource_access_time = sum(end - start for start, end in model.resource_access)
    
    # Calculate the partition delay
    partition_delay = total_time_period - total_resource_access_time
    
    return partition_delay