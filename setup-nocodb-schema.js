const axios = require('axios');

// Configuration
const ODOO_CONFIG = {
  url: 'https://erp.unipack.asia',
  db: 'unipack',
  username: 'hello@unipack.asia',
  apiKey: '8452eb0dc0dc4a3e1bcf8aae9c5cce53b0cd41f4'
};

const NOCODB_CONFIG = {
  url: 'https://noco.unipack.asia',
  token: '8uOsEZklg_xyCEA4sQDwa6gzm2UAhG6rgl7jcYuM',
  baseId: 'pkd6y355yqn7w9d'
};

// NocoDB API Helper
class NocoDBAPI {
  constructor(config) {
    this.baseUrl = `${config.url}/api/v2`;
    this.token = config.token;
    this.baseId = config.baseId;
    this.headers = {
      'xc-token': this.token,
      'Content-Type': 'application/json'
    };
  }

  async getTables() {
    const response = await axios.get(
      `${this.baseUrl}/meta/bases/${this.baseId}/tables`,
      { headers: this.headers }
    );
    return response.data.list;
  }

  async deleteTable(tableId) {
    await axios.delete(
      `${this.baseUrl}/meta/tables/${tableId}`,
      { headers: this.headers }
    );
  }

  async createTable(tableName, columns) {
    const response = await axios.post(
      `${this.baseUrl}/meta/bases/${this.baseId}/tables`,
      {
        table_name: tableName,
        title: tableName,
        columns: columns
      },
      { headers: this.headers }
    );
    return response.data;
  }

  async insertRecords(tableId, records) {
    if (records.length === 0) return;

    // Insert in batches of 100
    for (let i = 0; i < records.length; i += 100) {
      const batch = records.slice(i, i + 100);
      await axios.post(
        `${this.baseUrl}/tables/${tableId}/records`,
        batch,
        { headers: this.headers }
      );
      console.log(`  Inserted ${Math.min(i + 100, records.length)}/${records.length} records`);
    }
  }
}

// Odoo API Helper
class OdooAPI {
  constructor(config) {
    this.url = config.url;
    this.db = config.db;
    this.username = config.username;
    this.apiKey = config.apiKey;
    this.uid = null;
  }

  async authenticate() {
    // Odoo API key authentication - we'll use the API key directly in requests
    this.uid = 2; // Will be validated in requests
    console.log('✓ Using Odoo API Key authentication');
    return true;
  }

  async searchRead(model, domain = [], fields = []) {
    try {
      const response = await axios.post(
        `${this.url}/jsonrpc`,
        {
          jsonrpc: '2.0',
          method: 'call',
          params: {
            service: 'object',
            method: 'execute',
            args: [
              this.db,
              this.uid,
              this.apiKey,
              model,
              'search_read',
              domain,
              fields
            ]
          },
          id: Math.floor(Math.random() * 1000000)
        },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.error) {
        throw new Error(response.data.error.data.message || 'Odoo API error');
      }

      return response.data.result || [];
    } catch (error) {
      console.error(`Error fetching ${model}:`, error.message);
      throw error;
    }
  }
}

// Main setup function
async function setupSchema() {
  console.log('🚀 Starting NocoDB Schema Setup\n');

  const noco = new NocoDBAPI(NOCODB_CONFIG);
  const odoo = new OdooAPI(ODOO_CONFIG);

  try {
    // Step 1: Authenticate with Odoo
    console.log('📡 Connecting to Odoo...');
    await odoo.authenticate();

    // Step 2: Fetch data from Odoo
    console.log('\n📊 Fetching reference data from Odoo...');

    console.log('  - Fetching states...');
    const states = await odoo.searchRead('res.country.state', [['country_id.code', '=', 'IN']], ['id', 'name', 'code']);
    console.log(`    ✓ Found ${states.length} states`);

    console.log('  - Fetching countries...');
    const countries = await odoo.searchRead('res.country', [], ['id', 'name', 'code']);
    console.log(`    ✓ Found ${countries.length} countries`);

    console.log('  - Fetching taxes...');
    const taxes = await odoo.searchRead('account.tax', [['type_tax_use', '=', 'sale']], ['id', 'name', 'amount', 'type_tax_use']);
    console.log(`    ✓ Found ${taxes.length} taxes`);

    console.log('  - Fetching UOMs...');
    const uoms = await odoo.searchRead('uom.uom', [], ['id', 'name']);
    console.log(`    ✓ Found ${uoms.length} UOMs`);

    console.log('  - Fetching product categories...');
    const categories = await odoo.searchRead('product.category', [], ['id', 'name', 'parent_id']);
    console.log(`    ✓ Found ${categories.length} categories`);

    // Step 3: Delete existing tables
    console.log('\n🗑️  Deleting existing tables...');
    const existingTables = await noco.getTables();
    for (const table of existingTables) {
      console.log(`  - Deleting ${table.title}...`);
      await noco.deleteTable(table.id);
    }
    console.log('  ✓ All existing tables deleted');

    // Step 4: Create reference tables
    console.log('\n📋 Creating reference tables...');

    // 4.1 ref_states
    console.log('  - Creating ref_states...');
    const statesTable = await noco.createTable('ref_states', [
      { column_name: 'id', title: 'ID', uidt: 'ID', pk: true },
      { column_name: 'name', title: 'Name', uidt: 'SingleLineText' },
      { column_name: 'code', title: 'Code', uidt: 'SingleLineText' },
      { column_name: 'odoo_id', title: 'Odoo ID', uidt: 'Number' }
    ]);
    await noco.insertRecords(statesTable.id, states.map(s => ({
      name: s.name,
      code: s.code,
      odoo_id: s.id
    })));
    console.log(`    ✓ Created and populated with ${states.length} records`);

    // 4.2 ref_countries
    console.log('  - Creating ref_countries...');
    const countriesTable = await noco.createTable('ref_countries', [
      { column_name: 'id', title: 'ID', uidt: 'ID', pk: true },
      { column_name: 'name', title: 'Name', uidt: 'SingleLineText' },
      { column_name: 'code', title: 'Code', uidt: 'SingleLineText' },
      { column_name: 'odoo_id', title: 'Odoo ID', uidt: 'Number' }
    ]);
    await noco.insertRecords(countriesTable.id, countries.map(c => ({
      name: c.name,
      code: c.code,
      odoo_id: c.id
    })));
    console.log(`    ✓ Created and populated with ${countries.length} records`);

    // 4.3 ref_categories
    console.log('  - Creating ref_categories...');
    const categoriesTable = await noco.createTable('ref_categories', [
      { column_name: 'id', title: 'ID', uidt: 'ID', pk: true },
      { column_name: 'name', title: 'Name', uidt: 'SingleLineText' },
      { column_name: 'odoo_id', title: 'Odoo ID', uidt: 'Number' },
      { column_name: 'parent_odoo_id', title: 'Parent Odoo ID', uidt: 'Number' }
    ]);
    await noco.insertRecords(categoriesTable.id, categories.map(cat => ({
      name: cat.name,
      odoo_id: cat.id,
      parent_odoo_id: cat.parent_id ? cat.parent_id[0] : null
    })));
    console.log(`    ✓ Created and populated with ${categories.length} records`);

    // 4.4 ref_taxes
    console.log('  - Creating ref_taxes...');
    const taxesTable = await noco.createTable('ref_taxes', [
      { column_name: 'id', title: 'ID', uidt: 'ID', pk: true },
      { column_name: 'name', title: 'Name', uidt: 'SingleLineText' },
      { column_name: 'rate', title: 'Rate', uidt: 'Number' },
      { column_name: 'odoo_id', title: 'Odoo ID', uidt: 'Number' }
    ]);
    await noco.insertRecords(taxesTable.id, taxes.map(t => ({
      name: t.name,
      rate: t.amount,
      odoo_id: t.id
    })));
    console.log(`    ✓ Created and populated with ${taxes.length} records`);

    // 4.5 ref_gst_treatment
    console.log('  - Creating ref_gst_treatment...');
    const gstTreatmentTable = await noco.createTable('ref_gst_treatment', [
      { column_name: 'id', title: 'ID', uidt: 'ID', pk: true },
      { column_name: 'name', title: 'Name', uidt: 'SingleLineText' },
      { column_name: 'odoo_code', title: 'Odoo Code', uidt: 'SingleLineText' }
    ]);
    const gstTreatments = [
      { name: 'Registered Business - Regular', odoo_code: 'registered_business_regular' },
      { name: 'Registered Business - Composition', odoo_code: 'registered_business_composition' },
      { name: 'Unregistered Business', odoo_code: 'unregistered' },
      { name: 'Consumer', odoo_code: 'consumer' },
      { name: 'Overseas', odoo_code: 'overseas' },
      { name: 'Special Economic Zone', odoo_code: 'special_economic_zone' }
    ];
    await noco.insertRecords(gstTreatmentTable.id, gstTreatments);
    console.log(`    ✓ Created and populated with ${gstTreatments.length} records`);

    // 4.6 ref_uom
    console.log('  - Creating ref_uom...');
    const uomTable = await noco.createTable('ref_uom', [
      { column_name: 'id', title: 'ID', uidt: 'ID', pk: true },
      { column_name: 'name', title: 'Name', uidt: 'SingleLineText' },
      { column_name: 'odoo_id', title: 'Odoo ID', uidt: 'Number' }
    ]);
    await noco.insertRecords(uomTable.id, uoms.map(u => ({
      name: u.name,
      odoo_id: u.id
    })));
    console.log(`    ✓ Created and populated with ${uoms.length} records`);

    // Step 5: Create code generator tables (empty for now)
    console.log('\n🔢 Creating code generator tables...');

    console.log('  - Creating code_machine_name...');
    await noco.createTable('code_machine_name', [
      { column_name: 'code', title: 'Code', uidt: 'SingleLineText', pk: true },
      { column_name: 'name', title: 'Name', uidt: 'SingleLineText' }
    ]);
    console.log('    ✓ Created (empty - awaiting data upload)');

    console.log('  - Creating code_machine_size...');
    await noco.createTable('code_machine_size', [
      { column_name: 'code', title: 'Code', uidt: 'SingleLineText', pk: true },
      { column_name: 'description', title: 'Description', uidt: 'SingleLineText' }
    ]);
    console.log('    ✓ Created (empty - awaiting data upload)');

    console.log('  - Creating code_assembly_type...');
    await noco.createTable('code_assembly_type', [
      { column_name: 'code', title: 'Code', uidt: 'SingleLineText', pk: true },
      { column_name: 'name', title: 'Name', uidt: 'SingleLineText' }
    ]);
    console.log('    ✓ Created (empty - awaiting data upload)');

    console.log('  - Creating code_kit_type...');
    await noco.createTable('code_kit_type', [
      { column_name: 'code', title: 'Code', uidt: 'SingleLineText', pk: true },
      { column_name: 'name', title: 'Name', uidt: 'SingleLineText' }
    ]);
    console.log('    ✓ Created (empty - awaiting data upload)');

    console.log('  - Creating code_product_type...');
    await noco.createTable('code_product_type', [
      { column_name: 'code', title: 'Code', uidt: 'SingleLineText', pk: true },
      { column_name: 'name', title: 'Name', uidt: 'SingleLineText' }
    ]);
    console.log('    ✓ Created (empty - awaiting data upload)');

    // Step 6: Create Product Master table
    console.log('\n📦 Creating Product Master table...');
    await noco.createTable('Products', [
      { column_name: 'id', title: 'ID', uidt: 'ID', pk: true },
      { column_name: 'product_code', title: 'Product Code', uidt: 'SingleLineText' },
      { column_name: 'product_name', title: 'Product Name', uidt: 'SingleLineText' },
      { column_name: 'product_type', title: 'Product Type', uidt: 'SingleSelect', dtxp: 'Storable,Service,Consumable' },
      { column_name: 'invoicing_policy', title: 'Invoicing Policy', uidt: 'SingleSelect', dtxp: 'Ordered Qty,Delivered Qty' },
      { column_name: 'sales_price', title: 'Sales Price', uidt: 'Currency', dtxp: 'INR' },
      { column_name: 'purchase_price', title: 'Purchase Price', uidt: 'Currency', dtxp: 'INR' },
      { column_name: 'hsn_code', title: 'HSN Code', uidt: 'SingleLineText' },
      { column_name: 'barcode', title: 'Barcode', uidt: 'SingleLineText' },
      { column_name: 'description', title: 'Description', uidt: 'LongText' },
      { column_name: 'is_active', title: 'Is Active', uidt: 'Checkbox', cdf: 'true' },
      { column_name: 'odoo_id', title: 'Odoo ID', uidt: 'Number' },
      { column_name: 'sync_status', title: 'Sync Status', uidt: 'SingleSelect', dtxp: 'Pending,Synced,Error', cdf: 'Pending' }
    ]);
    console.log('  ✓ Product Master created');

    // Step 7: Create Contact Master table
    console.log('\n👥 Creating Contact Master table...');
    await noco.createTable('Contacts', [
      { column_name: 'id', title: 'ID', uidt: 'ID', pk: true },
      { column_name: 'customer_id', title: 'Customer ID', uidt: 'SingleLineText' },
      { column_name: 'customer_name', title: 'Customer Name', uidt: 'SingleLineText' },
      { column_name: 'contact_person', title: 'Contact Person', uidt: 'SingleLineText' },
      { column_name: 'designation', title: 'Designation', uidt: 'SingleLineText' },
      { column_name: 'mobile', title: 'Mobile', uidt: 'PhoneNumber' },
      { column_name: 'phone', title: 'Phone', uidt: 'PhoneNumber' },
      { column_name: 'email', title: 'Email', uidt: 'Email' },
      { column_name: 'website', title: 'Website', uidt: 'URL' },
      { column_name: 'address_line_1', title: 'Address Line 1', uidt: 'SingleLineText' },
      { column_name: 'address_line_2', title: 'Address Line 2', uidt: 'SingleLineText' },
      { column_name: 'city', title: 'City', uidt: 'SingleLineText' },
      { column_name: 'pincode', title: 'Pincode', uidt: 'SingleLineText' },
      { column_name: 'gst_number', title: 'GST Number', uidt: 'SingleLineText' },
      { column_name: 'pan_number', title: 'PAN Number', uidt: 'SingleLineText' },
      { column_name: 'customer_type', title: 'Customer Type', uidt: 'SingleSelect', dtxp: 'B2B,B2C' },
      { column_name: 'is_customer', title: 'Is Customer', uidt: 'Checkbox', cdf: 'true' },
      { column_name: 'is_vendor', title: 'Is Vendor', uidt: 'Checkbox', cdf: 'false' },
      { column_name: 'notes', title: 'Notes', uidt: 'LongText' },
      { column_name: 'odoo_id', title: 'Odoo ID', uidt: 'Number' },
      { column_name: 'sync_status', title: 'Sync Status', uidt: 'SingleSelect', dtxp: 'Pending,Synced,Error', cdf: 'Pending' }
    ]);
    console.log('  ✓ Contact Master created');

    console.log('\n✅ Schema setup completed successfully!\n');
    console.log('📝 Summary:');
    console.log(`  - ref_states: ${states.length} records`);
    console.log(`  - ref_countries: ${countries.length} records`);
    console.log(`  - ref_categories: ${categories.length} records`);
    console.log(`  - ref_taxes: ${taxes.length} records`);
    console.log(`  - ref_gst_treatment: ${gstTreatments.length} records`);
    console.log(`  - ref_uom: ${uoms.length} records`);
    console.log('  - 5 code generator tables (empty)');
    console.log('  - Products table (empty)');
    console.log('  - Contacts table (empty)');
    console.log('\n🎯 Next steps:');
    console.log('  1. Upload machine and code reference master data');
    console.log('  2. Configure table relationships/links in NocoDB UI');
    console.log('  3. Test product code generation');

  } catch (error) {
    console.error('\n❌ Error during setup:', error.message);
    if (error.response) {
      console.error('Response data:', JSON.stringify(error.response.data, null, 2));
    }
    process.exit(1);
  }
}

// Run setup
setupSchema();
