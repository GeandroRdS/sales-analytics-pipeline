# Sales Order Automation & Analytics Pipeline

End-to-end portfolio project demonstrating business process automation, data integration, and business intelligence.

The project simulates a B2B distributor that receives hundreds of customer purchase orders through a consolidated PDF document.

The solution automatically extracts and validates these orders, integrates information from Excel and a simulated ERP REST API, stores processed data in PostgreSQL, and provides business analytics through Power BI.

## Project Architecture

```text
Purchase Orders PDF
        |
        v
  Python Extraction
        |
        v
 Standardized Orders
        |
   +----+----+
   |         |
   v         v
 Excel     ERP API
   |         |
   +----+----+
        |
        v
    Validation
        |
   +----+----+
   |         |
   v         v
Approved   Rejected
   |         |
   +----+----+
        |
        v
    PostgreSQL
        |
   +----+----+
   |         |
   v         v
 Excel    Power BI
 Output   Analytics
```

## Planned Stack

- Python
- Pandas
- Excel
- PDF Processing
- REST APIs
- PostgreSQL
- SQL
- Power BI
- Docker
- Git

## Business Scale

The synthetic environment will simulate approximately:

- 35 customers
- 8 sales representatives
- 150 products
- 300 purchase orders
- 1,500+ order items

All data used in this project is synthetic.

## Project Status

🚧 Under development.

See [Project Scope](docs/project_scope.md) for the complete business requirements.