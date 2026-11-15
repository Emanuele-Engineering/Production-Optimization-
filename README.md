# Production-Optimization-
End-to-end supply chain model (Python, Gurobi, Operations Research). Maximizes profitability by optimizing production, distribution, inventory, and workforce allocation under operational constraints .
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

