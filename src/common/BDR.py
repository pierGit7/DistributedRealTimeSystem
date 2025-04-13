from SRPModel import SRPModel


class BDR:
    def __init__(self, model: SRPModel, time_interval: int,):
        self.model = model
        self.time_interval = time_interval
        
    def get_availability_factor(self):
        """
        Calculate the availability factor for a given SRP model.
        
        Args:
            model (SRPModel): The SRP model to calculate the availability factor for.
            
        Returns:
            float: The availability factor for the given SRP model.
        """
        # Calculate the total time period
        total_time_period = self.model.period
        
        # Calculate the total resource access time
        total_resource_access_time = sum(end - start for start, end in self.model.resource_access)
        
        # Calculate the availability factor
        availability_factor = total_resource_access_time / total_time_period
        
        return availability_factor

    def get_partition_delay(self):
        """
        Calculate the partition delay for a given SRP model.
        
        Args:
            model (SRPModel): The SRP model to calculate the partition delay for.
            
        Returns:
            float: The partition delay for the given SRP model.
        """
        partition_delay = 0
        supply_bound_function = self.get_supply_bound_function(self.get_supply_function(), self.time_interval)
        
        return partition_delay

    def get_supply_function(self):
        """
        Calculate the supply function for a given SRP model.
        
        Args:
            model (SRPModel): The SRP model to calculate the supply function for.
            time_interval (int): The time interval to calculate the supply function over.
            
        Returns:
            dict[int, list[int]]: The supply function for the given SRP model.
        """
        supply_function: dict[int, list[int]] = {
            end: [0 for _ in range(self.time_interval)] for start, end in self.model.resource_access
        }
        starting_time =  [end for start, end in self.model.resource_access]
        
        for end_key in starting_time:
            period_tracker =  end_key - 1
            for time in range(self.time_interval):
                period_tracker += 1
                if period_tracker == self.model.period:
                    period_tracker = 0
                supply_function[end_key][time] = supply_function[end_key][time - 1]
                for start, end in self.model.resource_access:
                    if start < period_tracker <= end and time != 0:
                        supply_function[end_key][time] = supply_function[end_key][time - 1] + 1
                        break
        
        return supply_function

    def get_supply_bound_function(self, supply_function: dict[int, list[int]], time_interval: int):
        """
        Calculate the supply bound function for a given supply function.
        
        Args:
            supply_function (dict[int, list[int]]): The supply function to calculate the supply bound function for.
            
        Returns:
            list[int]: The supply bound function for the given supply function.
        """
        supply_function = self.get_supply_function()
        values = supply_function.values()
        supply_bound_function = [0 for _ in range(self.time_interval)]
        for i in range(self.time_interval):
            supply_bound_function[i] = min([value[i] for value in values])
        return supply_bound_function
    
    
if __name__ == "__main__":
    # Example usage
    model = SRPModel(resource_access=[(1, 2), (5, 7)], period=8)
    bdr = BDR(model=model, time_interval=25)
    
    print("Availability Factor:", bdr.get_availability_factor())
    print("Partition Delay:", bdr.get_partition_delay())
    print("Supply Function:", bdr.get_supply_function())
    print("Supply Bound Function:", bdr.get_supply_bound_function(bdr.get_supply_function(), 20))
    import matplotlib.pyplot as plt

    # Plot the supply function
    supply_function = bdr.get_supply_function()
    for end_key, values in supply_function.items():
        plt.plot(range(bdr.time_interval), values, label=f"End Key {end_key}")
    plt.plot(range(bdr.time_interval), bdr.get_supply_bound_function(supply_function, bdr.time_interval), label="Supply Bound Function", linestyle='--')
    plt.title("Supply Function")
    plt.xlabel("Time")
    plt.ylabel("Supply")
    plt.legend()
    plt.grid(True)
    plt.show()