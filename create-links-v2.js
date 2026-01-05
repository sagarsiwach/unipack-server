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

// Table IDs
const tables = {
  'Products': 'm8x4ihkfchc5xvq',
  'Contacts': 'mnerlqtgcp7qjaq',
  'ref_categories': 'm4psx940j9yiiz7',
  'ref_taxes': 'm2cyxnun3vgia9y',
  'ref_uom': 'm9pcyf8bq45l0r4',
  'ref_states': 'mmtia5ulhyub0hs',
  'ref_countries': 'm9tbth1tgqmnx9m',
  'ref_gst_treatment': 'm5jrwce5q01d28z',
  'code_machine_name': 'mu9mjh1jrfhmgrf',
  'code_machine_size': 'mvci42ad7c70m1l',
  'code_assembly_type': 'md7o7vwrhgqpipz',
  'code_kit_type': 'm9t2ahfub7posjk',
  'code_product_type': 'mfzsfouywktgrsr'
};

async function createLink(fromTable, toTable, columnTitle, description) {
  try {
    console.log(`Creating link: ${columnTitle} from ${fromTable} to ${toTable}...`);

    // Try the API v2 format
    const response = await axios.post(
      `${NOCODB_CONFIG.url}/api/v2/meta/tables/${tables[fromTable]}/columns`,
      {
        title: columnTitle,
        column_name: columnTitle.toLowerCase().replace(/ /g, '_'),
        uidt: 'Links',
        description: description,
        parentId: tables[toTable],
        childId: tables[fromTable],
        type: 'mm'
      },
      { headers }
    );

    console.log(`  ✓ Created successfully`);
    return response.data;
  } catch (error) {
    console.error(`  ✗ Failed:`, error.response?.data || error.message);

    // Try alternative format
    try {
      console.log(`  Trying alternative format...`);
      const response2 = await axios.post(
        `${NOCODB_CONFIG.url}/api/v2/meta/tables/${tables[fromTable]}/columns`,
        {
          title: columnTitle,
          uidt: 'LinkToAnotherRecord',
          description: description,
          fk_related_model_id: tables[toTable],
          fk_model_id: tables[fromTable],
          type: 'mm'
        },
        { headers }
      );
      console.log(`  ✓ Created with alternative format`);
      return response2.data;
    } catch (error2) {
      console.error(`  ✗ Alternative format also failed:`, error2.response?.data || error2.message);
      throw error2;
    }
  }
}

async function createAllLinks() {
  console.log('🔗 Creating table links...\n');

  const links = [
    // Product Master links
    { from: 'Products', to: 'ref_categories', title: 'Product Category', desc: 'Select product category from Odoo categories' },
    { from: 'Products', to: 'ref_taxes', title: 'Sales Tax', desc: 'Default tax rate for sales (typically 18% GST)' },
    { from: 'Products', to: 'ref_taxes', title: 'Purchase Tax', desc: 'Default tax rate for purchases' },
    { from: 'Products', to: 'ref_uom', title: 'Unit of Measure', desc: 'Sales unit (NOS, PCS, SET, etc.)' },
    { from: 'Products', to: 'code_machine_name', title: 'Machine Type', desc: 'Machine type for product code (4 digits)' },
    { from: 'Products', to: 'code_machine_size', title: 'Machine Size', desc: 'Machine size for product code (4 digits, default: 9000)' },
    { from: 'Products', to: 'code_assembly_type', title: 'Assembly Type', desc: 'Assembly type for product code (2 digits, default: 10)' },
    { from: 'Products', to: 'code_kit_type', title: 'Kit Type', desc: 'Kit type for product code (2 digits, default: 00)' },
    { from: 'Products', to: 'code_product_type', title: 'Product Type Code', desc: 'Product type for code generation' },

    // Contact Master links
    { from: 'Contacts', to: 'ref_states', title: 'State', desc: 'Select state from Indian states' },
    { from: 'Contacts', to: 'ref_countries', title: 'Country', desc: 'Select country (default: India)' },
    { from: 'Contacts', to: 'ref_gst_treatment', title: 'GST Treatment', desc: 'GST classification' }
  ];

  let successCount = 0;
  let failCount = 0;

  for (const link of links) {
    try {
      await createLink(link.from, link.to, link.title, link.desc);
      successCount++;
      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 500));
    } catch (error) {
      failCount++;
    }
  }

  console.log(`\n📊 Summary: ${successCount} succeeded, ${failCount} failed`);

  if (successCount === links.length) {
    console.log('✅ All links created successfully!');
  } else if (successCount > 0) {
    console.log('⚠️  Some links created, but some failed. Please check the errors above.');
  } else {
    console.log('❌ Failed to create links. Manual UI setup may be required.');
  }
}

createAllLinks();
