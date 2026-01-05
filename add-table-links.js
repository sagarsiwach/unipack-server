const axios = require('axios');

const NOCODB_CONFIG = {
  url: 'https://noco.unipack.asia',
  token: '8uOsEZklg_xyCEA4sQDwa6gzm2UAhG6rgl7jcYuM',
  baseId: 'pkd6y355yqn7w9d'
};

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

  async getTableByTitle(title) {
    const tables = await this.getTables();
    return tables.find(t => t.title === title);
  }

  async addLinkColumn(tableId, columnData) {
    try {
      const response = await axios.post(
        `${this.baseUrl}/meta/tables/${tableId}/columns`,
        columnData,
        { headers: this.headers }
      );
      return response.data;
    } catch (error) {
      console.error(`Error adding link column:`, error.response?.data || error.message);
      throw error;
    }
  }

  async updateTable(tableId, data) {
    try {
      const response = await axios.patch(
        `${this.baseUrl}/meta/tables/${tableId}`,
        data,
        { headers: this.headers }
      );
      return response.data;
    } catch (error) {
      console.error(`Error updating table:`, error.response?.data || error.message);
      throw error;
    }
  }

  async getColumns(tableId) {
    try {
      const response = await axios.get(
        `${this.baseUrl}/meta/tables/${tableId}/columns`,
        { headers: this.headers }
      );
      return response.data.list;
    } catch (error) {
      console.error(`Error getting columns:`, error.response?.data || error.message);
      throw error;
    }
  }

  async updateColumn(columnId, data) {
    try {
      const response = await axios.patch(
        `${this.baseUrl}/meta/columns/${columnId}`,
        data,
        { headers: this.headers }
      );
      return response.data;
    } catch (error) {
      console.error(`Error updating column:`, error.response?.data || error.message);
      throw error;
    }
  }
}

async function addTableLinks() {
  console.log('🔗 Setting up table relationships and beautification...\n');

  const noco = new NocoDBAPI(NOCODB_CONFIG);

  try {
    // Define table metadata
    const tableMetadata = {
      'Products': {
        title: 'Product Master',
        description: 'Master product catalog with pricing, specifications, and Odoo sync status'
      },
      'Contacts': {
        title: 'Contact Master',
        description: 'Customer and vendor contact database with address and GST information'
      },
      'ref_states': {
        title: 'States (Reference)',
        description: 'Indian states reference with Odoo mapping'
      },
      'ref_countries': {
        title: 'Countries (Reference)',
        description: 'Countries reference with Odoo mapping'
      },
      'ref_categories': {
        title: 'Product Categories (Reference)',
        description: 'Product categories synced from Odoo'
      },
      'ref_taxes': {
        title: 'Tax Rates (Reference)',
        description: 'GST and tax rates from Odoo'
      },
      'ref_gst_treatment': {
        title: 'GST Treatment Types (Reference)',
        description: 'GST treatment classification for customers'
      },
      'ref_uom': {
        title: 'Units of Measure (Reference)',
        description: 'Standard units of measure from Odoo'
      },
      'code_machine_name': {
        title: 'Machine Names (Code Generator)',
        description: 'Machine type codes for product code generation'
      },
      'code_machine_size': {
        title: 'Machine Sizes (Code Generator)',
        description: 'Machine size codes for product code generation'
      },
      'code_assembly_type': {
        title: 'Assembly Types (Code Generator)',
        description: 'Assembly type codes for product code generation'
      },
      'code_kit_type': {
        title: 'Kit Types (Code Generator)',
        description: 'Kit type codes for product code generation'
      },
      'code_product_type': {
        title: 'Product Types (Code Generator)',
        description: 'Product type codes for product code generation'
      }
    };

    // Get all table IDs
    console.log('📋 Fetching and updating table information...');
    const tables = {};
    const tableNames = Object.keys(tableMetadata);

    for (const name of tableNames) {
      const table = await noco.getTableByTitle(name);
      if (table) {
        tables[name] = table.id;

        // Update table metadata
        const meta = tableMetadata[name];
        await noco.updateTable(table.id, {
          title: meta.title,
          description: meta.description
        });

        console.log(`  ✓ ${meta.title} (${table.id})`);
      } else {
        console.log(`  ✗ ${name}: Not found`);
      }
    }

    // Add links to Products table
    console.log('\n📦 Adding links to Product Master table...');

    console.log('  - Adding Category link...');
    await noco.addLinkColumn(tables['Products'], {
      title: 'Product Category',
      description: 'Select product category from Odoo categories',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['ref_categories'],
      childId: tables['Products']
    });

    console.log('  - Adding Sales Tax link...');
    await noco.addLinkColumn(tables['Products'], {
      title: 'Sales Tax',
      description: 'Default tax rate for sales (typically 18% GST)',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['ref_taxes'],
      childId: tables['Products']
    });

    console.log('  - Adding Purchase Tax link...');
    await noco.addLinkColumn(tables['Products'], {
      title: 'Purchase Tax',
      description: 'Default tax rate for purchases',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['ref_taxes'],
      childId: tables['Products']
    });

    console.log('  - Adding Unit of Measure link...');
    await noco.addLinkColumn(tables['Products'], {
      title: 'Unit of Measure',
      description: 'Sales unit (NOS, PCS, SET, etc.)',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['ref_uom'],
      childId: tables['Products']
    });

    // Add code generator links to Products table
    console.log('  - Adding Machine Name link (for code generation)...');
    await noco.addLinkColumn(tables['Products'], {
      title: 'Machine Type',
      description: 'Machine type for product code (4 digits)',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['code_machine_name'],
      childId: tables['Products']
    });

    console.log('  - Adding Machine Size link (for code generation)...');
    await noco.addLinkColumn(tables['Products'], {
      title: 'Machine Size',
      description: 'Machine size for product code (4 digits, default: 9000)',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['code_machine_size'],
      childId: tables['Products']
    });

    console.log('  - Adding Assembly Type link (for code generation)...');
    await noco.addLinkColumn(tables['Products'], {
      title: 'Assembly Type',
      description: 'Assembly type for product code (2 digits, default: 10)',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['code_assembly_type'],
      childId: tables['Products']
    });

    console.log('  - Adding Kit Type link (for code generation)...');
    await noco.addLinkColumn(tables['Products'], {
      title: 'Kit Type',
      description: 'Kit type for product code (2 digits, default: 00)',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['code_kit_type'],
      childId: tables['Products']
    });

    console.log('  - Adding Product Type Code link (for code generation)...');
    await noco.addLinkColumn(tables['Products'], {
      title: 'Product Type Code',
      description: 'Product type for code generation (Spare/Machine/Purchase)',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['code_product_type'],
      childId: tables['Products']
    });

    console.log('  ✓ All links added to Product Master');

    // Add links to Contacts table
    console.log('\n👥 Adding links to Contact Master table...');

    console.log('  - Adding State link...');
    await noco.addLinkColumn(tables['Contacts'], {
      title: 'State',
      description: 'Select state from Indian states',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['ref_states'],
      childId: tables['Contacts']
    });

    console.log('  - Adding Country link...');
    await noco.addLinkColumn(tables['Contacts'], {
      title: 'Country',
      description: 'Select country (default: India)',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['ref_countries'],
      childId: tables['Contacts']
    });

    console.log('  - Adding GST Treatment link...');
    await noco.addLinkColumn(tables['Contacts'], {
      title: 'GST Treatment',
      description: 'GST classification (Registered/Unregistered/Overseas etc.)',
      uidt: 'Links',
      type: 'mm',
      parentId: tables['ref_gst_treatment'],
      childId: tables['Contacts']
    });

    console.log('  ✓ All links added to Contact Master');

    console.log('\n✅ All table relationships created successfully!\n');
    console.log('📝 Summary:');
    console.log('  Products table links:');
    console.log('    - category → ref_categories');
    console.log('    - sales_tax → ref_taxes');
    console.log('    - purchase_tax → ref_taxes');
    console.log('    - uom → ref_uom');
    console.log('    - machine_name → code_machine_name');
    console.log('    - machine_size → code_machine_size');
    console.log('    - assembly_type → code_assembly_type');
    console.log('    - kit_type → code_kit_type');
    console.log('    - product_type_code → code_product_type');
    console.log('  Contacts table links:');
    console.log('    - state → ref_states');
    console.log('    - country → ref_countries');
    console.log('    - gst_treatment → ref_gst_treatment');

  } catch (error) {
    console.error('\n❌ Error:', error.message);
    if (error.response) {
      console.error('Response:', JSON.stringify(error.response.data, null, 2));
    }
    process.exit(1);
  }
}

addTableLinks();
