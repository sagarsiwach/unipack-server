const axios = require('axios');

const NOCODB_CONFIG = {
  url: 'https://noco.unipack.asia',
  token: '8uOsEZklg_xyCEA4sQDwa6gzm2UAhG6rgl7jcYuM',
  baseId: 'pkd6y355yqn7w9d'
};

const headers = {
  'xc-token': NOCODB_CONFIG.token,
  'Content-Type': 'application/json'
};

async function createProductBuilder() {
  console.log('🏗️  Creating Product Builder table...\n');

  try {
    // Create Product Builder table
    const response = await axios.post(
      `${NOCODB_CONFIG.url}/api/v2/meta/bases/${NOCODB_CONFIG.baseId}/tables`,
      {
        table_name: 'Product_Builder',
        title: 'Product Builder',
        description: 'Generate product codes and create products',
        columns: [
          { column_name: 'id', title: 'ID', uidt: 'ID', pk: true },
          { column_name: 'product_name', title: 'Product Name', uidt: 'SingleLineText' },
          { column_name: 'sequence', title: 'Sequence Number', uidt: 'Number', dtxp: '4' },
          { column_name: 'generated_code', title: 'Generated Product Code', uidt: 'SingleLineText' },
          { column_name: 'description', title: 'Description', uidt: 'LongText' },
          {
            column_name: 'status',
            title: 'Status',
            uidt: 'SingleSelect',
            dtxp: 'Draft,Ready to Create,Created',
            cdf: 'Draft'
          },
          { column_name: 'notes', title: 'Notes', uidt: 'LongText' }
        ]
      },
      { headers }
    );

    const tableId = response.data.id;
    console.log(`✓ Product Builder table created: ${tableId}\n`);

    // Small delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Now add the link columns to code generator tables
    console.log('Adding links to code generator tables...\n');

    const links = [
      { title: 'Machine Type', targetTable: 'mu9mjh1jrfhmgrf', desc: 'Select machine type (4 digits)' },
      { title: 'Machine Size', targetTable: 'mvci42ad7c70m1l', desc: 'Select size (4 digits, default: 9000)' },
      { title: 'Assembly Type', targetTable: 'md7o7vwrhgqpipz', desc: 'Select assembly type (2 digits, default: 10)' },
      { title: 'Kit Type', targetTable: 'm9t2ahfub7posjk', desc: 'Select kit type (2 digits, default: 00)' },
      { title: 'Product Type', targetTable: 'mfzsfouywktgrsr', desc: 'Select product type' }
    ];

    for (const link of links) {
      try {
        console.log(`  - Adding ${link.title}...`);

        await axios.post(
          `${NOCODB_CONFIG.url}/api/v2/meta/tables/${tableId}/columns`,
          {
            title: link.title,
            uidt: 'LinkToAnotherRecord',
            description: link.desc,
            fk_related_model_id: link.targetTable,
            fk_model_id: tableId,
            type: 'bt'  // belongs-to (many-to-one)
          },
          { headers }
        );

        console.log(`    ✓ Created`);
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (error) {
        console.error(`    ✗ Failed:`, error.response?.data?.msg || error.message);
      }
    }

    console.log('\n✅ Product Builder table created successfully!\n');
    console.log('📋 Table Structure:');
    console.log('  Basic Fields:');
    console.log('    - Product Name (text)');
    console.log('    - Sequence Number (number, 4 digits)');
    console.log('    - Generated Product Code (text - will be auto-filled)');
    console.log('    - Description (long text)');
    console.log('    - Status (Draft/Ready to Create/Created)');
    console.log('    - Notes (long text)');
    console.log('  ');
    console.log('  Code Generator Links:');
    console.log('    - Machine Type → code_machine_names');
    console.log('    - Machine Size → code_machine_sizes');
    console.log('    - Assembly Type → code_assembly_types');
    console.log('    - Kit Type → code_kit_types');
    console.log('    - Product Type → code_product_types');
    console.log('');
    console.log('🎯 Next Steps:');
    console.log('  1. Create a formula/automation to generate product code');
    console.log('  2. Add automation to create product in Product Master');
    console.log('  3. Fix Product Master links (many-to-many → many-to-one)');

  } catch (error) {
    console.error('\n❌ Error:', error.message);
    if (error.response) {
      console.error('Response:', JSON.stringify(error.response.data, null, 2));
    }
    process.exit(1);
  }
}

createProductBuilder();
