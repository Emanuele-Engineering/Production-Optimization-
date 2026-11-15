# Production-Optimization-
End-to-end supply chain model (Python, Gurobi, Operations Research). Maximizes profitability by optimizing production, distribution, inventory, and workforce allocation under operational constraints.

# Marinero Supply Chain Optimization (MILP)

## 📌 Project Overview
This repository contains a Mixed-Integer Linear Programming (MILP) model developed in Python using **Gurobi** to optimize the end-to-end supply chain and production network for a manufacturing company (Marinero). The model simultaneously optimizes production planning, facility location (activation), distribution routing, inventory management, and workforce allocation to maximize total net profit over a 6-month horizon.

## 🎯 Business Problem & Objectives
The company operates 3 manufacturing plants and must distribute 5 products to 8 potential sales centers across two distinct markets (Customers 'C' and Firms 'F'). 

**Key challenges addressed:**
- **Facility Activation:** Deciding which plants and exactly 7 out of 8 sales centers to keep open, accounting for fixed operational costs.
- **Parametric Demand:** Modeling price-elastic demand and market seasonality.
- **Market Prioritization:** Enforcing a business rule where the higher-margin 'C' market must be satisfied before the 'F' market.
- **Resource Constraints:** Balancing manpower availability, working hours, raw materials, and energy consumption.

## 🛠️ Mathematical Modeling & Tech Stack
- **Solver:** Gurobi Optimizer
- **Language:** Python (`gurobipy`)
- **Formulation:** Big-M MILP
- **Key Variables:** Production quantities, shipment flows, binary facility activation, inventory levels, and integer workforce sizing.
- **Constraints:** Flow conservation, inventory balance equations, Big-M logical constraints for facility activation, capacity limits, and market priority rules.

---

## 📐 Mathematical Formulation

### 1. Sets and Indices
- **i** ∈ {1, ..., I}: Manufacturing plants
- **j** ∈ {1, ..., J}: Sales centers
- **n** ∈ {1, ..., N}: Products
- **k** ∈ {1, ..., K}: Months (Planning horizon: 6 months)
- **m** ∈ {1, ..., M}: Raw materials
- **mkt** ∈ {C, F}: Markets (Customers, Firms)

### 2. Parameters

**Costs & Revenues:**
- `raw_cons[n,m]`, `raw_rate[m]`: Raw material consumption and cost rate
- `pow_cons[i,n]`, `pow_rate`: Energy consumption and cost rate
- `fix_prod[i]`, `fix_dist[j]`: Fixed operational costs for plants and centers
- `price[n,mkt]`: Fixed selling prices (determined via SAT simulation)
- `tran_cost[i,j]`, `vol[n]`: Transport cost per unit and product volume
- `inv_cost[n,j]`: Inventory holding cost
- `salary[i]`: Worker salary

**Demand & Manpower:**
- `η[n,j]`, `θ[n,mkt]`, `φ[mkt,k]`: Demand elasticity, price sensitivity, and seasonality parameters
- `man_cons[i,n]`: Manpower consumption (hours per unit)
- `hours[i]`: Available working hours per worker
- `LB[i]`, `UB[i]`: Lower and upper bounds for workforce sizing

### 3. Decision Variables
- **x[i,k,n]** ≥ 0: Production quantity of product n at plant i in month k
- **y[i,j,k,n]** ≥ 0: Shipment quantity of product n from plant i to center j in month k
- **sales[n,mkt,j,k]** ≥ 0: Sales quantity of product n in market mkt at center j in month k
- **inv[j,n,k]** ≥ 0: Inventory level of product n at center j at the end of month k
- **workers[i,k]** ∈ ℤ⁺: Number of workers assigned to plant i in month k
- **z_plant[i]** ∈ {0,1}: Binary variable for plant activation
- **z_center[j]** ∈ {0,1}: Binary variable for sales center activation

### 4. Objective Function

**Maximize Total Profit = Total Revenues - Total Costs**
