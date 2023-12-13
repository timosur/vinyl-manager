import datetime
import pandas as pd


def calculate_weights(row, inputs):
    weight = 0

    # Adjust weight based on conditions
    date = datetime.date.today()
    year_current = date.year

    # Modelling year filter - Current and -1 years (+1 weight)
    if (year_current - 1) <= row['date_year'] <= year_current:
        weight += 1

    # Modelling year filter - 2 years old (+0 weight)
    if row['date_year'] == (year_current - 2):
        weight += 0

    # Modelling year filter - >2 years old (-1.5 weight)
    if row['date_year'] < (year_current - 2):
        weight += -1.5

    # Number of WTGs filter - Within +-35% (+1 weight)
    if (inputs.wtgCapacity * 0.65) <= row['number_of_wtgs'] <= (inputs.wtgCapacity * 1.35):
        weight += 1

    # OEM filter - Name match (+1 weight)
    if row['oem'] == inputs.oem:
        weight += 1

    # WTG capacity filter - Within +-2 MW (+1 weight)
    if (inputs.wtgCapacity - 2) <= row['wtg_capacity_mw'] <= (inputs.wtgCapacity + 2):
        weight += 1

    # Region filter - Name match (+1 weight)
    if row['region'] == inputs.region:
        weight += 1

    # Foundation filter - Name match (+1 weight)
    if row['foundation_type'] == inputs.foundationType:
        weight += 1

    # Substation filter - Number match (+1 weight)
    if row['number_of_substations'] == inputs.numberOfSubstations:
        weight += 1

    # Distance filter - Within +-20% (+1 weight)
    if (inputs.distanceFromOMPort * 0.8) <= row['distance_from_port_km'] <= (inputs.distanceFromOMPort * 1.2):
        weight += 1

    # Lifetime filter - Within +-3 years (+1 weight)
    if (float(inputs.operationalPeriod) - 3) <= row['lifetime_years'] <= (float(inputs.operationalPeriod) + 3):
        weight += 1

    # Project stage filter - Prospect Tool modelled (+0 weight)
    if row['project_development_stage'] == "Prospect":
        weight += 0

    # Project stage filter - Bid stage (+0.5 weight)
    if row['project_development_stage'] == "Bid":
        weight += 0.5

    # Project stage filter - FID stage (+1 weight)
    if row['project_development_stage'] == "FID":
        weight += 1

    # Add more conditions as per your logic
    return weight

def perform_calculations(df: pd.DataFrame, inputs) -> dict:
    # 1. Filter out rows where the weight is less than 4
    df.loc[df['Weight'] < 4, 'Weight'] = 0

    # 2. Check if the total weight is zero and return an error message if it is
    total_weight = df['Weight'].sum()
    if total_weight == 0:
        return "Error: There are no projects matching the inputs enough."

    # 3. Calculate the weighted average cost per WTG and cost per MW
    annual_cost_per_WTG = (df['annual_cost_per_wtg_eur'] * df['Weight']).sum() / total_weight
    annual_cost_per_MW = (df['annual_cost_per_mw_eur'] * df['Weight']).sum() / total_weight

    # Convert variables to appropriate data types
    annual_cost_per_WTG = float(annual_cost_per_WTG)
    numberOfWTGs = int(inputs.numberOfWTGs)
    wtgCapacity = float(inputs.wtgCapacity)
    operationalPeriod = float(inputs.operationalPeriod)

    # 4. Calculate total project cost based on the number of WTGs, total capacity, and calculate the average
    lifetime_cost_WTG = annual_cost_per_WTG * numberOfWTGs * operationalPeriod
    lifetime_cost_MW = annual_cost_per_MW * numberOfWTGs * wtgCapacity * operationalPeriod
    lifetime_cost_average = (lifetime_cost_WTG + lifetime_cost_MW) / 2

    # 5. Add overheads, including contingency based on the O&M global strategy
    GlobalStrategyContingencyDict = {
        "A": 0.03,
        "B": 0.04,
        "C": 0.04,
        "D": 0.05
    }

    RWEContingency = GlobalStrategyContingencyDict[inputs.omGlobalStrategy]

    # Check if the project lifetime exceeds the WTG design life
    if float(inputs.operationalPeriod) > 25:
        PostDesignLifeYrs = float(inputs.operationalPeriod) - 25
    else:
        PostDesignLifeYrs = 0

    PostDesignLifeContingency = (PostDesignLifeYrs / float(inputs.operationalPeriod)) * 0.01

    # Check what's RWE's shareholding level for margin
    if float(inputs.rweShareholding) == 100:
        RWEMargin = 0
    else:
        RWEMargin = 0.1

    # Create a dictionary and add the FOP, depending on the global strategy
    GlobalStrategyFOPDict = {
        "A": 0.02,
        "B": 0.03,
        "C": 0.03,
        "D": 0.04
    }

    # Check what's RWE's shareholding level for FOP
    if float(inputs.rweShareholding) == 100:
        RWEFOP = 0
    else:
        RWEFOP = GlobalStrategyFOPDict[inputs.omGlobalStrategy]

    # Now add the overheads on top of the base costs
    lifetime_cost_average = lifetime_cost_average * (
            1 + RWEContingency + PostDesignLifeContingency + RWEMargin + RWEFOP)

    # 6. Calculate weighted average time-based and production-based availability
    TBA_result = (df['tba_percent'] * df['Weight']).sum() / total_weight
    PBA_result = (df['pba_percent'] * df['Weight']).sum() / total_weight

    # Format results as needed
    TBA_result_formatted = f'{TBA_result:.1%}'
    PBA_result_formatted = f'{PBA_result:.1%}'

    # Re-Calculate the project's annual cost per WTG, annual cost per MW, based on the lifetime cost
    wtg_cost_per_year = (lifetime_cost_average / (float(inputs.numberOfWTGs) * float(inputs.operationalPeriod)))
    mw_cost_per_year = (
            lifetime_cost_average / (
            float(inputs.numberOfWTGs) * float(inputs.wtgCapacity) * float(inputs.operationalPeriod)))

    # Return the calculated results
    return {
        "lifetime_cost_average": lifetime_cost_average,
        "wtg_cost_per_year": wtg_cost_per_year,
        "mw_cost_per_year": mw_cost_per_year,
        "tba": TBA_result_formatted,
        "pba": PBA_result_formatted
    }