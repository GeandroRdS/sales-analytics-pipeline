# Sales Order Automation & Analytics Pipeline

## Overview

This project simulates a real-world B2B order processing workflow.

A fictional technology distributor receives a consolidated PDF document containing hundreds of customer purchase orders.

Processing these orders manually requires employees to read the document, identify customers and products, validate quantities, consult product information, check prices and inventory, and prepare the information for further processing.

The goal of this project is to automate this workflow and transform the resulting operational data into useful business analytics.

## Business Problem

The manual order processing workflow creates several challenges:

- Repetitive data entry
- High processing time
- Human error
- Manual product validation
- Manual inventory verification
- Difficulty identifying invalid orders
- Limited visibility into processing errors
- Fragmented sales information

## Proposed Solution

The project implements an end-to-end order automation and analytics pipeline.

The solution will:

1. Read a consolidated PDF containing customer purchase orders.
2. Identify individual orders inside the document.
3. Extract customer, order and item information.
4. Convert the extracted information into a standardized structure.
5. Integrate product information from an Excel file.
6. Retrieve customer, pricing and inventory information from a simulated ERP REST API.
7. Validate orders according to business rules.
8. Separate approved and rejected orders.
9. Generate an Excel processing report.
10. Store processed information in PostgreSQL.
11. Build an analytical data model using SQL.
12. Provide business analytics through Power BI.

## Data Sources

### Purchase Orders PDF

A consolidated PDF containing multiple customer purchase orders.

The document contains information such as:

- Purchase order number
- Order date
- Customer identification
- Product codes
- Product descriptions
- Requested quantities

### Product Master Excel

An Excel spreadsheet containing complementary product information:

- Product code
- Description
- Category
- Brand
- Units per case

### ERP REST API

A simulated ERP API providing operational information such as:

- Customer information
- Customer status
- Product status
- Product prices
- Inventory availability

## Simulated Business Scale

The synthetic environment contains approximately:

- 35 business customers
- 8 sales representatives
- 150 products
- 8 product categories
- 6 product brands
- 300 purchase orders
- 1,500+ order items

The dataset covers transactions between January 2025 and August 2026.

All companies, customers, products, transactions and documents used in this project are entirely synthetic.

## Business Rules

Orders are validated before being approved.

Validation includes:

- Customer exists
- Customer is active
- Product exists
- Product is active
- Quantity is greater than zero
- Inventory is sufficient
- Quantity respects package configuration
- Purchase order has not already been processed

## Processing Status

Possible validation results include:

- APPROVED
- PRODUCT_NOT_FOUND
- CUSTOMER_NOT_FOUND
- INACTIVE_PRODUCT
- INACTIVE_CUSTOMER
- INSUFFICIENT_STOCK
- INVALID_QUANTITY
- INVALID_PACKAGE_QUANTITY
- DUPLICATE_ORDER
- PARSING_ERROR

## Outputs

The automation produces:

### Excel Processing Report

An Excel workbook containing:

- Approved Orders
- Rejected Orders
- Processing Summary

### PostgreSQL Database

Stores processed operational information and supports analytical queries.

### Power BI Dashboard

Provides sales and order-processing analytics.

## Planned Analytics

The final dashboard will provide metrics such as:

- Revenue
- Orders Processed
- Approved Orders
- Rejected Orders
- Approval Rate
- Average Order Value
- Units Sold
- Revenue by Customer
- Revenue by Seller
- Revenue by Product
- Revenue by Category
- Order Processing Errors
- Sales Evolution

## Technology Stack

- Python
- Pandas
- PDF processing
- Excel
- REST API
- PostgreSQL
- SQL
- Power BI
- Docker
- Git
- GitHub