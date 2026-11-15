import gurobipy as gp
from gurobipy import GRB

# ==========================================
# 1. DATA PARSING FUNCTIONS
# ==========================================
# Note: These functions parse specific CSV structures. 
# In a production environment, using pandas is recommended.

def read_raw_materials(filepath="raw.csv"):
    """Reads raw material consumption, amounts, and electricity rates."""
    with open(filepath, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]
    
    consumption = []
    for i in range(3, 8):
        row = lines[i].split(';')
        try:
            values = [float(x) for x in row[1:5]]
            consumption.append(values)
        except ValueError:
            continue
            
    amount = []
    for i in range(11, 14):
        row = lines[i].split(';')
        try:
            values = [float(x) for x in row[1:5]]
            amount.append(values)
        except ValueError:
            continue
            
    try:
        high_rate = [float(x) for x in lines[16].split(';')[1:5]]
        low_rate = [float(x) for x in lines[17].split(';')[1:5]]
    except Exception:
        high_rate = [0, 0, 0, 0]
        low_rate = [0, 0, 0, 0]
        
    return consumption, amount, high_rate, low_rate

def read_power_data(filepath="power.csv"):
    """Reads power consumption, plant capacities, and electricity rates."""
    with open(filepath, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]
        
    consumption = []
    for i in range(3, 6):
        row = lines[i].split(';')
        consumption.append([float(x) for x in row[1:6]])
        
    plant_names = ["Jesolo", "Cosenza", "Cagliari"]
    amount = []
    for plant in plant_names:
        for line in lines:
            if plant in line:
                row = line.split(';')
                try:
                    amount.append(float(row[-1]))
                except (ValueError, IndexError):
                    amount.append(0.0)
                break
                
    low_rate = float(lines[8].split(';')[1])
    high_rate = float(lines[9].split(';')[1])
    
    return consumption, amount, low_rate, high_rate

def read_fixed_costs(filepath="fixed_costs.csv"):
    """Reads fixed production and distribution costs."""
    with open(filepath, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]
        
    production = []
    for i in range(2, 5):
        row = lines[i].split(';')
        try:
            production.append(float(row[1]))
        except (ValueError, IndexError):
            continue
            
    distribution = []
    for i in range(7, len(lines)):
        row = lines[i].split(';')
        try:
            values = [float(x) for x in row[0:8]]
            distribution = values
            break
        except ValueError:
            continue
            
    return production, distribution

def read_manpower_data(filepath="manpower.csv"):
    """Reads manpower consumption, working hours, salaries, and worker bounds."""
    with open(filepath, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]
        
    plants = ["Jesolo", "Cosenza", "Cagliari"]
    hour_consumption = []
    for line in lines:
        row = line.split(';')
        if row[0] in plants:
            try:
                values = [float(x) for x in row[1:6]]
                hour_consumption.append(values)
            except Exception:
                continue
        if len(hour_consumption) == 3:
            break
            
    working_hours, salaries, lower_bounds, upper_bounds = [], [], [], []
    found_section = False
    
    for idx, line in enumerate(lines):
        if 'working hours' in line.lower():
            found_section = True
            start = idx + 1
            break
            
    if found_section:
        for i in range(start, start + 3):
            row = lines[i].split(';')
            numerics = []
            for cell in row[1:]:
                try:
                    numerics.append(float(cell))
                except ValueError:
                    continue
            if len(numerics) == 4:
                break
                
        if len(numerics) == 4:
            working_hours.append(numerics[0])
            salaries.append(numerics[1])
            lower_bounds.append(int(numerics[2]))
            upper_bounds.append(int(numerics[3]))
        else:
            working_hours.append(0)
            salaries.append(0)
            lower_bounds.append(0)
            upper_bounds.append(1000)
            
    return hour_consumption, working_hours, salaries, lower_bounds, upper_bounds

def read_transport_data(filepath="transport.csv"):
    """Reads transport costs, product volumes, and inventory holding costs."""
    with open(filepath, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]
        
    tran_cost = []
    for i in range(3, 6):
        row = lines[i].split(';')
        tran_cost.append([float(x) for x in row[1:9]])
        
    volumes = []
    for i in range(7, len(lines)):
        row = lines[i].split(';')
        if len(row) > 1:
            try:
                volumes.append(float(row[1]))
            except ValueError:
                continue
        if len(volumes) == 5:
            break
            
    inventory_costs = []
    inv_start = 11
    for i in range(inv_start, inv_start + 5):
        if i < len(lines):
            row = lines[i].split(';')
            vals = [float(x) for x in row[1:9]]
            inventory_costs.append(vals)
            
    return tran_cost, volumes, inventory_costs

def read_demand_parameters(filepath="demand.csv"):
    """Reads demand parameters (eta, phi, theta) and sets/products names."""
    eta, phi, theta = {}, {}, {}
    product_names, center_names, months = [], [], []
    
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        center_names = [name.strip() for name in lines[2].split(';')[1:] if name.strip()]
        
        # ETA and product names
        for i in range(3, 8):
            row = lines[i].split(';')
            product = row[0].strip()
            product_names.append(product)
            for j, value in enumerate(row[1:len(center_names) + 1]):
                center = center_names[j]
                try:
                    eta[(product, center)] = float(value)
                except ValueError:
                    eta[(product, center)] = 0.0
                    
        # PHI (Market seasonality)
        phi_header = None
        for idx, line in enumerate(lines):
            if "Firms amount parameters" in line:
                phi_header = lines[idx].split(';')
                phi_start = idx + 1
                break
                
        idx_firms = [i for i, x in enumerate(phi_header) if "Firms" in x][0]
        idx_customers = [i for i, x in enumerate(phi_header) if "Customers" in x][0]
        
        for i in range(phi_start, phi_start + 6):
            row = lines[i].split(';')
            month = row[0].strip()
            months.append(month)
            phi[('F', month)] = float(row[idx_firms]) if len(row) > idx_firms and row[idx_firms].strip() else 0.0
            phi[('C', month)] = float(row[idx_customers]) if len(row) > idx_customers and row[idx_customers].strip() else 0.0
            
        # THETA (Price sensitivity)
        theta_header = None
        for idx, line in enumerate(lines):
            if "Firms Price Parameter" in line:
                theta_header = lines[idx].split(';')
                theta_start = idx + 1
                break
                
        idx_firms = [i for i, x in enumerate(theta_header) if "Firms" in x][0]
        idx_customers = [i for i, x in enumerate(theta_header) if "Customer" in x][0]
        
        for i in range(theta_start, theta_start + 5):
            row = lines[i].split(';')
            prod = row[0].strip()
            theta[('F', prod)] = float(row[idx_firms]) if len(row) > idx_firms and row[idx_firms].strip() else 0.0
            theta[('C', prod)] = float(row[idx_customers]) if len(row) > idx_customers and row[idx_customers].strip() else 0.0
            
    return eta, phi, theta, product_names, center_names, months


# ==========================================
# 2. DEMAND CALCULATION HELPER
# ==========================================
def calculate_demand(prod, mkt, center, month, eta, theta, phi, fixed_prices):
    """Calculates theoretical parametric demand based on price elasticity and seasonality."""
    # Advertising coefficient is set to 0 for this scenario
    if prod != 'frisbee':
        a = 1.5 if mkt == 'C' else 1.6
        prezzo = fixed_prices[(prod, mkt)]
        max_term = max(2 - prezzo / theta[(mkt, prod)], 0)
        return eta[(prod, center)] * (max_term ** a) * (phi[(mkt, month)] / 10)
    else:
        a = 1.5 if mkt == 'C' else 1.6
        return eta[(prod, center)] * (2.1 ** a) * (phi[(mkt, month)] / 10)


# ==========================================
# 3. MAIN OPTIMIZATION MODEL
# ==========================================
def main():
    print("Loading data from CSV files...")
    # Load parameters
    eta, phi, theta, product_names, center_names, months_phi = read_demand_parameters("demand.csv")
    tran_cost, volumes, inventory_costs = read_transport_data()
    power_consumption, power_amount, power_low_rate, power_high_rate = read_power_data()
    raw_consumption, raw_amount, raw_high_rate, raw_low_rate = read_raw_materials()
    manpower_consumption, working_hours, salaries, lower_bounds, upper_bounds = read_manpower_data()
    production_fixed_costs, distribution_fixed_costs = read_fixed_costs()

    # Sets and Dimensions
    markets = ['C', 'F']
    num_months = 6
    num_products = 5
    num_plants = 3
    num_centers = 8
    plant_names = ["Jesolo", "Cosenza", "Cagliari"]

    # Fixed Prices (Determined via SAT simulation, Frisbee is a free promotional item)
    fixed_prices = {
        ('deckchair', 'C'): 48, ('deckchair', 'F'): 32,
        ('beach umbrella', 'C'): 58, ('beach umbrella', 'F'): 42,
        ('sun bed', 'C'): 42, ('sun bed', 'F'): 28,
        ("director's chair", 'C'): 52, ("director's chair", 'F'): 34,
        ('frisbee', 'C'): 0, ('frisbee', 'F'): 0
    }

    # Pre-calculate Demand Dictionary to avoid redundant calculations in constraints
    demand_dict = {}
    for prod in product_names:
        for mkt in markets:
            for center in center_names:
                for month in months_phi:
                    demand_dict[(prod, mkt, center, month)] = calculate_demand(
                        prod, mkt, center, month, eta, theta, phi, fixed_prices
                    )

    # Initialize Gurobi Model
    model = gp.Model("Marinero_Supply_Chain_Optimization")

    # --- DECISION VARIABLES ---
    x = model.addVars(num_plants, num_months, num_products, vtype=GRB.CONTINUOUS, name="Production")
    y = model.addVars(num_plants, num_centers, num_months, num_products, vtype=GRB.CONTINUOUS, name="Shipment")
    is_active_plant = model.addVars(num_plants, vtype=GRB.BINARY, name="IsPlantActive")
    is_active_center = model.addVars(num_centers, vtype=GRB.BINARY, name="IsCenterActive")
    sales = model.addVars(product_names, markets, center_names, months_phi, vtype=GRB.CONTINUOUS, name="Sales")
    inventory = model.addVars(num_centers, num_products, num_months, vtype=GRB.CONTINUOUS, name="Inventory")
    workers = model.addVars(num_plants, num_months, vtype=GRB.INTEGER, name="Workers")

    BIG_M = 1e6

    # --- CONSTRAINTS ---
    
    # 1. Plant & Center Activation (Big-M)
    for i in range(num_plants):
        for k in range(num_months):
            for n in range(num_products):
                model.addConstr(x[i, k, n] <= BIG_M * is_active_plant[i], name=f"PlantActivation_{i}_{k}_{n}")

    for j in range(num_centers):
        for k in range(num_months):
            for n in range(num_products):
                model.addConstr(
                    gp.quicksum(y[i, j, k, n] for i in range(num_plants)) <= BIG_M * is_active_center[j],
                    name=f"CenterActivation_{j}_{k}_{n}"
                )

    # 2. Commercial Constraint: Exactly 7 out of 8 centers must be open
    model.addConstr(gp.quicksum(is_active_center[j] for j in range(num_centers)) == 7, name="MaxCentersOpen")

    # 3. Flow Conservation: No inventory at plants (Production = Shipment)
    for i in range(num_plants):
        for k in range(num_months):
            for n in range(num_products):
                shipment_sum = gp.quicksum(y[i, j, k, n] for j in range(num_centers))
                model.addConstr(x[i, k, n] == shipment_sum, name=f"FlowConservation_{i}_{k}_{n}")

    # 4. Inventory Balance at Centers
    for j in range(num_centers):
        for n in range(num_products):
            for k in range(num_months):
                arrived = gp.quicksum(y[i, j, k, n] for i in range(num_plants))
                sold = gp.quicksum(sales[product_names[n], mkt, center_names[j], months_phi[k]] for mkt in markets)
                
                if k == 0:
                    model.addConstr(inventory[j, n, k] == arrived - sold, name=f"InitInventory_{j}_{n}_{k}")
                else:
                    model.addConstr(inventory[j, n, k] == inventory[j, n, k-1] + arrived - sold, name=f"InvBalance_{j}_{n}_{k}")

    # 5. Sales Upper Bounds (Cannot sell more than theoretical demand)
    for prod in product_names:
        for mkt in markets:
            for center in center_names:
                for month in months_phi:
                    model.addConstr(
                        sales[prod, mkt, center, month] <= demand_dict[(prod, mkt, center, month)],
                        name=f"DemandLimit_{prod}_{mkt}_{center}_{month}"
                    )

    # 6. Availability Constraints & Market Priority (Market 'C' has priority over 'F')
    for k, month in enumerate(months_phi):
        for j, center in enumerate(center_names):
            for n, prod in enumerate(product_names):
                if k == 0:
                    availability = gp.quicksum(y[i, j, k, n] for i in range(num_plants))
                else:
                    availability = gp.quicksum(y[i, j, k, n] for i in range(num_plants)) + inventory[j, n, k-1]
                
                # Priority Market 'C'
                model.addConstr(sales[prod, 'C', center, month] <= availability, name=f"Avail_C_{prod}_{center}_{month}")
                
                # Secondary Market 'F' gets the remainder
                model.addConstr(
                    sales[prod, 'F', center, month] <= availability - sales[prod, 'C', center, month],
                    name=f"Avail_F_{prod}_{center}_{month}"
                )

    # 7. Manpower Constraints
    for i in range(num_plants):
        for k in range(num_months):
            # If plant is closed, workers must be 0. If open, respect lower/upper bounds.
            model.addConstr(workers[i, k] <= upper_bounds[i] * is_active_plant[i], name=f"WorkersClosed_{i}_{k}")
            model.addConstr(workers[i, k] >= lower_bounds[i] * is_active_plant[i], name=f"WorkersLB_{i}_{k}")
            model.addConstr(workers[i, k] <= upper_bounds[i], name=f"WorkersUB_{i}_{k}")
            
            # Production capacity based on available working hours
            total_hours = gp.quicksum(x[i, k, n] * manpower_consumption[i][n] for n in range(num_products))
            model.addConstr(total_hours <= workers[i, k] * working_hours[i], name=f"CapacityLimit_{i}_{k}")

    # --- OBJECTIVE FUNCTION: MAXIMIZE PROFIT ---
    
    # Revenues
    revenue = gp.quicksum(
        fixed_prices[(prod, mkt)] * sales[prod, mkt, center, month]
        for prod in product_names for mkt in markets for center in center_names for month in months_phi
    )
    
    # Costs
    costs = 0
    
    # Raw Material Costs (Low Rate)
    for i in range(num_plants):
        for m in range(4):
            total_consumed = gp.quicksum(raw_consumption[n][m] * x[i, k, n] for n in range(num_products) for k in range(num_months))
            costs += raw_low_rate[m] * total_consumed
            
    # Energy Costs (Low Rate)
    for i in range(num_plants):
        for k in range(num_months):
            total_energy = gp.quicksum(power_consumption[i][n] * x[i, k, n] for n in range(num_products))
            costs += power_low_rate * total_energy
            
    # Manpower Costs
    for i in range(num_plants):
        for k in range(num_months):
            costs += workers[i, k] * salaries[i]
            
    # Transport Costs
    for i in range(num_plants):
        for j in range(num_centers):
            for k in range(num_months):
                for n in range(num_products):
                    costs += tran_cost[i][j] * volumes[n] * y[i, j, k, n]
                    
    # Inventory Holding Costs
    for j in range(num_centers):
        for k in range(num_months):
            for n in range(num_products):
                inv_cost = inventory_costs[n][j] if (n < len(inventory_costs) and j < len(inventory_costs[n])) else 0.0
                costs += inv_cost * inventory[j, n, k]
                
    # Fixed Costs (Plants & Centers)
    for i in range(num_plants):
        costs += production_fixed_costs[i] * is_active_plant[i]
    for j in range(num_centers):
        costs += distribution_fixed_costs[j] * is_active_center[j]

    # Set Objective
    model.setObjective(revenue - costs, GRB.MAXIMIZE)

    # --- SOLVE & EXPORT RESULTS ---
    print("\nOptimizing model...")
    model.optimize()

    if model.status == GRB.OPTIMAL:
        print(f"\n=== OPTIMAL SOLUTION FOUND ===")
        print(f"Total Optimal Profit: € {model.ObjVal:,.2f}\n")
        
        months_names = ["April", "May", "June", "July", "August", "September"]
        
        # 1. Production Plan
        print("--- PRODUCTION PLAN BY PLANT AND MONTH ---")
        for k in range(num_months):
            print(f"\n[{months_names[k]}]")
            print(f"{'Plant':<15}" + "".join([f"{prod:<18}" for prod in product_names]))
            print("-" * 100)
            for i in range(num_plants):
                row_str = f"{plant_names[i]:<15}"
                for n in range(num_products):
                    produced = sum(y[i, j, k, n].X for j in range(num_centers))
                    row_str += f"{produced:<18.2f}"
                print(row_str)

        # 2. Distribution Strategy
        print("\n--- DISTRIBUTION STRATEGY TO SALES CENTERS ---")
        for k in range(num_months):
            for n in range(num_products):
                print(f"\n[{months_names[k]} | {product_names[n]}]")
                print(" " * 15 + "".join([f"{c:>12}" for c in center_names]))
                for i in range(num_plants):
                    row_str = f"{plant_names[i]:<15}"
                    for j in range(num_centers):
                        row_str += f"{y[i, j, k, n].X:>12.2f}"
                    print(row_str)

        # 3. Fixed Prices Used
        print("\n--- FIXED PRICES APPLIED ---")
        profitable_products = product_names[:4]
        for prod in profitable_products:
            for mkt in markets:
                print(f"  Product: {prod:<15} | Market: {mkt} --> Price: € {fixed_prices[(prod, mkt)]:.2f}")

        # 4. Advertising Investments
        print("\n--- ADVERTISING INVESTMENTS ---")
        print("  (Set to 0 across all months and markets for this simulation scenario)")

        # 5. Workforce Planning
        print("\n--- WORKFORCE PLANNING (Workers per Plant/Month) ---")
        for k in range(num_months):
            print(f"\n[{months_names[k]}]")
            for i in range(num_plants):
                print(f"  {plant_names[i]}: {workers[i, k].X:.0f} workers")
                
    else:
        print("\nNo optimal solution found. Check model feasibility.")

if __name__ == "__main__":
    main()