# NocoDB Table Linking Guide

## 📋 Overview
This guide will help you create relationships between tables in NocoDB UI.

---

## 🔗 PART 1: Link Product Master Table

### Step 1: Open Product Master Table
1. Go to https://noco.unipack.asia
2. Open the **Product Master** table

### Step 2: Add Link Columns (9 total)

For each link below, follow these steps:
- Click the **+** button (Add Column) on the right
- Select **Links** as column type
- Configure as shown below

---

#### Link 1: Product Category
- **Column Name**: `Product Category`
- **Link To**: `Product Categories (Reference)`
- **Relation Type**: Many to Many
- **Description**: Select product category from Odoo categories

#### Link 2: Sales Tax
- **Column Name**: `Sales Tax`
- **Link To**: `Tax Rates (Reference)`
- **Relation Type**: Many to Many
- **Description**: Default tax rate for sales (typically 18% GST)

#### Link 3: Purchase Tax
- **Column Name**: `Purchase Tax`
- **Link To**: `Tax Rates (Reference)`
- **Relation Type**: Many to Many
- **Description**: Default tax rate for purchases

#### Link 4: Unit of Measure
- **Column Name**: `Unit of Measure`
- **Link To**: `Units of Measure (Reference)`
- **Relation Type**: Many to Many
- **Description**: Sales unit (NOS, PCS, SET, etc.)

#### Link 5: Machine Type (Code Generator)
- **Column Name**: `Machine Type`
- **Link To**: `Machine Names (Code Generator)`
- **Relation Type**: Many to Many
- **Description**: Machine type for product code (4 digits)

#### Link 6: Machine Size (Code Generator)
- **Column Name**: `Machine Size`
- **Link To**: `Machine Sizes (Code Generator)`
- **Relation Type**: Many to Many
- **Description**: Machine size for product code (4 digits, default: 9000)

#### Link 7: Assembly Type (Code Generator)
- **Column Name**: `Assembly Type`
- **Link To**: `Assembly Types (Code Generator)`
- **Relation Type**: Many to Many
- **Description**: Assembly type for product code (2 digits, default: 10)

#### Link 8: Kit Type (Code Generator)
- **Column Name**: `Kit Type`
- **Link To**: `Kit Types (Code Generator)`
- **Relation Type**: Many to Many
- **Description**: Kit type for product code (2 digits, default: 00)

#### Link 9: Product Type Code (Code Generator)
- **Column Name**: `Product Type Code`
- **Link To**: `Product Types (Code Generator)`
- **Relation Type**: Many to Many
- **Description**: Product type for code generation (Spare/Machine/Purchase)

---

## 👥 PART 2: Link Contact Master Table

### Step 1: Open Contact Master Table
1. Open the **Contact Master** table

### Step 2: Add Link Columns (3 total)

#### Link 1: State
- **Column Name**: `State`
- **Link To**: `States (Reference)`
- **Relation Type**: Many to Many
- **Description**: Select state from Indian states

#### Link 2: Country
- **Column Name**: `Country`
- **Link To**: `Countries (Reference)`
- **Relation Type**: Many to Many
- **Description**: Select country (default: India)

#### Link 3: GST Treatment
- **Column Name**: `GST Treatment`
- **Link To**: `GST Treatment Types (Reference)`
- **Relation Type**: Many to Many
- **Description**: GST classification (Registered/Unregistered/Overseas etc.)

---

## ✅ Verification Checklist

After completing all links, verify:

### Product Master (9 links):
- [ ] Product Category → Product Categories (Reference)
- [ ] Sales Tax → Tax Rates (Reference)
- [ ] Purchase Tax → Tax Rates (Reference)
- [ ] Unit of Measure → Units of Measure (Reference)
- [ ] Machine Type → Machine Names (Code Generator)
- [ ] Machine Size → Machine Sizes (Code Generator)
- [ ] Assembly Type → Assembly Types (Code Generator)
- [ ] Kit Type → Kit Types (Code Generator)
- [ ] Product Type Code → Product Types (Code Generator)

### Contact Master (3 links):
- [ ] State → States (Reference)
- [ ] Country → Countries (Reference)
- [ ] GST Treatment → GST Treatment Types (Reference)

---

## 🎯 Next Steps After Linking

1. **Test the relationships** by creating a sample product and contact
2. **Set up product code generation** formula/automation
3. **Configure Odoo sync** API endpoints
4. **Test end-to-end workflow**

---

## 📞 Need Help?

If you encounter issues:
1. Ensure all reference tables have data (check counts)
2. Verify table names match exactly
3. Use Many-to-Many for all relationships
4. Double-check column names for consistency
