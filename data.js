const stageLabels={
"1":{n:"Raw materials & biodiversity",t:"Upstream",c:"s1"},
"2":{n:"Extraction & ingredient manufacturing",t:"Midstream",c:"s2"},
"3":{n:"Formulation & contract manufacturing",t:"CDMO",c:"s3"},
"4":{n:"Branded products & IP",t:"Downstream",c:"s4"},
"5":{n:"Distribution & retail",t:"Go-to-market",c:"s5"},
"6":{n:"Regulatory & certification",t:"Cross-cutting",c:"s6"}
};
const secLabels={"1_raw_materials":"Raw materials","2_extraction_ingredients":"Extraction","3_cdmo_manufacturing":"CDMO","4_branded_products":"Branded","5_distribution_retail":"Distribution","6_regulatory_certification":"Regulatory"};
const D=[
{s:"1",g:"Palm oil feedstock",cs:[
{n:"Sime Darby Plantation",l:"Selangor",d:"World\u2019s largest palm oil company by planted area. Primary feedstock supplier for tocotrienol and carotenoid extraction. Supplies crude palm oil to ExcelVite, Carotech, and other downstream extractors.",c:["RSPO","MSPO"],w:"simedarbyplantation.com"},
{n:"FGV Holdings",l:"KL",d:"Malaysia\u2019s largest crude palm oil producer. Feedstock for oleochemical derivatives used in pharmaceutical and nutraceutical formulations. Listed on Bursa Malaysia.",c:["RSPO","MSPO"],w:"fgvholdings.com"},
{n:"IOI Corporation",l:"Putrajaya",d:"Integrated palm oil and oleochemical producer. Specialty fats and oleochemicals feed into nutraceutical ingredient manufacturing. Global operations across 14 countries.",c:["RSPO"],w:"ioigroup.com"}
]},
{s:"1",g:"Cultivation & animal sourcing",cs:[
{n:"DXN Holdings (Cultivation)",l:"Kedah",d:"Vertically integrated Ganoderma (Lingzhi) mushroom cultivator. Owns mushroom farms, controls entire supply chain from spore to finished supplement. 20M+ distributors globally. Relisted Bursa May 2023.",c:["GMP","Halal","ISO"],w:"dxn2u.com",x:"4_branded_products"},
{n:"Happy Health",l:"",d:"Bird\u2019s nest manufacturer with own swiftlet nesting facilities. Handles harvesting, cleaning, processing and packaging of raw bird\u2019s nest into consumer products.",c:[],w:"",x:"3_cdmo_manufacturing"},
{n:"Halagel (M) Sdn Bhd",l:"",d:"Sole importer and distributor of Halal empty hard gelatin capsules and Halal food/pharmaceutical-grade bovine gelatin in Malaysia. Critical upstream supplier to capsule manufacturers.",c:["Halal"],w:"halagel.com.my",x:"5_distribution_retail"}
]},
{s:"2",g:"Tocotrienol / palm phytonutrients",cs:[
{n:"ExcelVite Sdn Bhd",l:"Perak",d:"Palm tocotrienol extraction specialist. Products: EVNol\u2122 and EVNol SupraBio\u2122 (natural full spectrum palm tocotrienol complex), EVTene\u2122 (mixed-carotene complex). Pharmaceutical-grade PIC/S cGMP manufacturing. Sustainable sourcing via RSPO/MSPO.",c:["PIC/S cGMP","HACCP","Halal","Kosher","RSPO","MSPO"],w:"excelvite.com"},
{n:"Carotech Berhad",l:"Perak",d:"Pioneer in natural tocotrienol and mixed carotene R&D since 1990s. Products: Tocomin\u00ae SupraBio\u2122 tocotrienol complex, carotenoid concentrates. Focus on cardiovascular, neuroprotection, and anti-aging applications.",c:["GMP"],w:"carotech.com"},
{n:"PhytoGaia Sdn Bhd",l:"",d:"Delivers clinically researched palm phytonutrients. Products: TocoGaia\u2122 branded tocotrienol complex. Focuses on bioavailability enhancement and clinical validation.",c:[],w:"",x:"4_branded_products"},
{n:"KLK OLEO",l:"",d:"Division of KLK Berhad. Products: DavosLife E3\u00ae tocotrienols and tocopherols derived from non-GMO Malaysian palm fruits. B2B ingredient supplier worldwide.",c:[],w:"klkoleo.com",x:"4_branded_products"},
{n:"Kunak Lipids",l:"Sabah",d:"Phytonutrient extraction plant in Sabah producing premium tocotrienol products from natural non-GMO oil palm. East Malaysian raw material sourcing.",c:[],w:"kunaklipids.com"},
{n:"Innovans Palm Industries",l:"",d:"Palm oil processor focusing on extracting antioxidant vitamin E constituents\u2014tocopherols and tocotrienols\u2014from crude palm oil.",c:[],w:"innovans.com.my"},
{n:"SD Guthrie Intl Nutrition",l:"",d:"Pioneer in palm-based tocotrienol manufacturing. Part of SD Guthrie (formerly Sime Darby Oils). Branded tocotrienol ingredients for the global supplement market.",c:[],w:""}
]},
{s:"2",g:"Tongkat Ali & botanical extracts",cs:[
{n:"Biotropics Malaysia Berhad",l:"Selangor",d:"Khazanah-backed national champion. Products: Physta\u00ae Tongkat Ali extract (co-developed with MIT), BioKesum\u2122 (cognitive health), SLP+\u00ae Kacip Fatimah, AVCO\u00ae (activated virgin coconut oil). 70+ patents, 57 clinical studies, USFDA-monitored facilities. 35+ countries.",c:["GMP","USFDA"],w:"biotropicsmalaysia.com",x:"3_cdmo_manufacturing"},
{n:"Rainforest Herbs",l:"Selangor",d:"Tongkat Ali extract specialist since 1994. Standardized eurycomanone content via HPLC. FRIM research collaboration. Distributed through Caring Pharmacy and independent pharmacies.",c:["Halal","NPRA","FRIM"],w:"rainforestherbs.com",x:"4_branded_products"},
{n:"LJack",l:"",d:"Direct manufacturer of standardized botanical powder extracts since 1998. Freeze-dried Tongkat Ali, Kacip Fatimah, and other Malaysian botanicals. Proprietary freeze-drying preserves bioactive compounds.",c:[],w:"ljack.com"},
{n:"Natherm Group",l:"Selangor",d:"Manufacturer and supplier of herbal extracts including Tongkat Ali extract powder. Halal-certified production line.",c:["Halal"],w:"natherm.com"},
{n:"CK Ingredient Sdn Bhd",l:"",d:"High-quality herbal extracts with maximum bioactive compounds retention. Standardized botanical ingredients for downstream manufacturers.",c:[],w:"ckingredient.com"},
{n:"Medika Natura",l:"",d:"Products: SKF7\u2122\u2014first Malaysian botanical extract with USFDA clearance. Evidence-based botanical drug development bridging traditional and modern medicine.",c:["USFDA"],w:"medikanatura.com"},
{n:"HP Ingredients",l:"US-MY",d:"Products: LJ100\u00ae branded Tongkat Ali for Western market. Exclusive distributor of Biotropics\u2019 Physta\u00ae in US/EU. 13+ human clinical trials since 2002.",c:["USFDA"],w:"hpingredients.com"},
{n:"Furley Bioextracts",l:"Selangor",d:"Herbal and botanical extraction for nutraceutical applications. GMP-certified extraction facility.",c:["GMP"],w:""},
{n:"Silver Roots",l:"",d:"Herbal extract supplier. Agro-based extraction of Malaysian botanicals.",c:[],w:"silverrootsagro.com"}
]},
{s:"2",g:"Food ingredients & specialty",cs:[
{n:"Bionutricia",l:"",d:"Pioneer in patented liposomal encapsulation technology for vitamins, minerals, amino acids. Improves bioavailability of active ingredients.",c:[],w:"bionutricia.com",x:"3_cdmo_manufacturing"},
{n:"Bionutricia Extract",l:"",d:"Top 3 biotechnology-based botanical extract manufacturer. Standardized plant extraction services with focus on consistency and potency.",c:[],w:"bionutriciaextract.com"},
{n:"Honeyberry International",l:"",d:"Halal food ingredients and extracts for F&B manufacturers. Flavoring, coloring, and functional ingredients.",c:["Halal"],w:"honeyberry.my"},
{n:"Nutra Choice",l:"Johor",d:"Nutraceutical ingredients supplier. End-to-end support from product inception through formulation to manufacturing. Also operates CDMO services.",c:[],w:"nutrachoice.com.my",x:"3_cdmo_manufacturing"},
{n:"Lipidchem Sdn Bhd",l:"Johor",d:"Lipid-based health ingredient manufacturer in Bandar Seri Alam, Johor.",c:[],w:""},
{n:"CS Leaflabs",l:"Selangor",d:"Nutraceutical tech startup. Specialty botanical ingredient development.",c:[],w:""},
{n:"Euryka Naturopathics",l:"Selangor",d:"Nutritional supplement ingredient development.",c:[],w:""},
{n:"Nutrachoice",l:"Selangor",d:"Herbal and botanical extracts in powder form with clinically proven functional benefits.",c:[],w:"nutrachoice.com.my"}
]},
{s:"3",g:"Selangor corridor \u2014 Shah Alam / PJ / Puchong / S. Buloh",cs:[
{n:"Hovid Berhad",l:"Perak",d:"Malaysia\u2019s largest pharma+nutra CDMO. 400+ products, 50+ countries. Products: Ho Yan Hor\u00ae herbal tea, Tocovid SupraBio\u00ae tocotrienol supplement. PIC/S member enables EU/Canada/Australia export.",c:["PIC/S GMP","Halal","HACCP"],w:"hovid.com",x:"4_branded_products"},
{n:"TCT Nutraceuticals",l:"Selangor",d:"Full-service OEM skincare & nutraceutical manufacturer in Puchong. Formulation, R&D, NPRA registration, packaging design, trademark registration. End-to-end concept to shelf.",c:["GMP","Halal","HACCP"],w:"tctgroup.com.my"},
{n:"Bionutricia Manufacturing",l:"Selangor",d:"Health food supplement OEM in Kota Damansara. Natural extracts (pandan, strawberry, berries), functional food powders. Natural food-based ingredient approach.",c:["GMP","HACCP","JAKIM Halal"],w:"bionutricia.com"},
{n:"Elma Food",l:"Selangor",d:"OEM health food manufacturer with quad-certification. Health supplements, functional foods, and beverages for private label.",c:["GMP","HACCP","FDA","Halal"],w:"elmafoodoem.com"},
{n:"Herbal Science",l:"Selangor",d:"Custom capsule manufacturing since 1995. Multiple GMP facilities in PJ. Formulates, designs, manufactures, validates, certifies nutraceutical products. Own branded lines.",c:["GMP"],w:"herbalscience.com.my",x:"4_branded_products"},
{n:"Phytes Biotek",l:"Selangor",d:"Biotropics\u2019 wholly-owned manufacturing subsidiary. Herbal extraction and production for Physta\u00ae, BioKesum\u2122, and other Biotropics ingredient lines.",c:["GMP"],w:""},
{n:"FORMULAB INDUSTRY",l:"Selangor",d:"OEM factory in Shah Alam. Helps entrepreneurs and startups build private label health supplements with low MOQ.",c:[],w:"founderoem.com"},
{n:"Ori Bionature",l:"Selangor",d:"Contract manufacturer in Puchong. Custom formulation capsules, tablets, powders. Known for quality standards and responsive timelines.",c:["GMP"],w:"oribionature.com"},
{n:"Nano Food",l:"Selangor",d:"OEM/ODM in Puchong. One-stop A-to-Z: formulation, production, packaging, NPRA registration. Health supplements, traditional medicine, functional foods.",c:[],w:"nanofood.com.my"},
{n:"NCS Science",l:"Selangor",d:"OEM/ODM/OBM since 2010 (formerly NGS Healthcare). Formulation to finished product across supplements, functional foods, personal care.",c:[],w:"ncs-science.com"},
{n:"Yanling NH",l:"Selangor",d:"Premier OEM pharma+nutra manufacturer with 30+ years experience. 1,000+ products. Soft gel, tablet, capsule, powder, granule, liquid. One of the most established CDMOs in Malaysia.",c:[],w:"yanlingnh.com"},
{n:"MORETH",l:"Selangor",d:"Full lifecycle: product conceptualization, formulation, development, NPRA registration, mass manufacturing. Also markets own branded products.",c:[],w:"moreth.com",x:"4_branded_products"},
{n:"EMQ Pack / EMQP",l:"Selangor",d:"Food supplement and functional beverage manufacturer in Shah Alam. Functional food powders, health drinks, supplement sachets.",c:["GMP","HACCP"],w:"emqpack.com"},
{n:"Advantic Nutraceuticals",l:"Selangor",d:"Hi-Tech Industrial Park manufacturer in Semenyih. Autonomous machinery and modern production lines.",c:["GMP"],w:""},
{n:"GN Neutriceuticals",l:"Selangor",d:"Health supplement manufacturer in UEP Industrial Park, Subang Jaya.",c:[],w:""},
{n:"Brand8 Nutraceutical",l:"Selangor",d:"NPRA-licensed nutraceutical manufacturer.",c:["GMP"],w:""},
{n:"ProduxPro",l:"Selangor",d:"OEM supplement manufacturer in PJ. Health supplements and skincare.",c:[],w:"produxpro.com.my"},
{n:"NeuHerbs Nutraceutical",l:"Selangor",d:"Healthcare OEM/ODM in Batu Caves. Functional food powder concepts\u2014sachets, premixes, instant health beverages.",c:[],w:"neuherbs.com.my"},
{n:"TST Bioceutical",l:"Selangor",d:"Bioceutical manufacturing.",c:[],w:""},
{n:"Top Green",l:"Selangor",d:"OEM for gut health supplements and functional foods. Probiotic formulations, green superfood powders, digestive health supplements.",c:[],w:"topgreenoem.com"},
{n:"NatusVincere",l:"KL",d:"OEM/ODM for health supplements, functional food & beverage, cosmetics, personal care. KKM registered.",c:["KKM"],w:""},
{n:"Golden-Mah Bird\u2019s Nest",l:"Selangor",d:"Bird\u2019s nest manufacturer, 30+ years. Bottled drinks, dried bird\u2019s nest, gift sets. Own NestTrend\u00ae brand.",c:[],w:"nesttrend.com.my",x:"4_branded_products"},
{n:"Novaxis Health",l:"KL",d:"Comprehensive supplement OEM solutions. Operations and technical expertise for private label production.",c:[],w:"novaxis.com.my"},
{n:"Amecrown Group",l:"KL",d:"OEM & private label premixed beverage manufacturer. Functional beverages, premix drinks.",c:[],w:"amecrown.com.my"},
{n:"Naturecare Group",l:"Selangor",d:"OEM functional food manufacturer in Kajang.",c:[],w:""},
{n:"Living Natural",l:"Selangor",d:"Skincare and personal care OEM/ODM in Shah Alam.",c:[],w:"livingnatural.com.my"},
{n:"MHP",l:"Selangor",d:"Organic health products, supplements, health drinks with OEM services. Own branded product lines.",c:[],w:"mhp2u.com",x:"4_branded_products"}
]},
{s:"3",g:"Penang & Northern hub",cs:[
{n:"Sky Nutraceuticals",l:"Penang",d:"One of the largest health product manufacturers in Penang. Est. ~2007. OEM dietary supplements. Health consultation services.",c:["Halal"],w:"skynutraceuticals.com"},
{n:"Dexchem Industries",l:"Penang",d:"Pharma and nutraceutical manufacturer in Bukit Mertajam. Human and veterinary health products.",c:[],w:"dexchem.com"},
{n:"Winwa Medical",l:"Penang",d:"50+ years pharmaceutical manufacturing in Penang. Health solutions spanning supplements and generics.",c:[],w:"winwamedical.com"},
{n:"Keko Group",l:"Penang",d:"OEM/ODM fruit-flavored sparkling beverage manufacturer. Functional drinks, one-stop solutions.",c:[],w:"kekogroup.com"},
{n:"Bio Care Supplements",l:"Kedah",d:"Health supplement manufacturer in Lunas. GMP certified.",c:["GMP"],w:""}
]},
{s:"3",g:"Johor cluster",cs:[
{n:"Softgel Manufacturing",l:"Johor",d:"Malaysia\u2019s first dedicated 100% plant-based softgel capsule manufacturer. Iskandar Halal Park, Pasir Gudang.",c:[],w:"softgelmanufacturing.com.my"},
{n:"Nestlin",l:"Johor",d:"Large-scale bird\u2019s nest processing, 20,000 sq ft facility. Advanced cleaning, processing, bottling technology.",c:[],w:"nestlin.my"},
{n:"Pharmanutri",l:"Johor",d:"Halal sports nutrition and health supplements. Protein, pre-workouts, mass gainers\u2014all halal certified.",c:["Halal"],w:"pharmanutri.com.my",x:"5_distribution_retail"},
{n:"HQ Nutraceuticals",l:"Johor",d:"At UTM Technovation Park, Skudai. University-linked R&D.",c:[],w:""},
{n:"Supervitamins",l:"Johor",d:"Vitamin and supplement manufacturer in Masai.",c:[],w:""},
{n:"LIQ Formulations",l:"Johor",d:"OEM/ODM health supplement manufacturer in Gelang Patah.",c:[],w:""},
{n:"Apex Biocare",l:"Johor",d:"Biocare company in Johor Bahru.",c:[],w:"apexbio.my"},
{n:"S.H. Uniflex",l:"Johor",d:"Traditional Chinese Medicine manufacturer. Heritage TCM production.",c:[],w:""}
]},
{s:"3",g:"Perak & Melaka",cs:[
{n:"Kotra Pharma",l:"Melaka",d:"Pharma + nutraceutical development, manufacturing, marketing. Dual CDMO with own branded products.",c:["GMP","Halal"],w:"kotrapharma.com",x:"4_branded_products"},
{n:"D&O Nutraceutical Mfg",l:"Perak",d:"OEM health and beauty drink manufacturer in Pengkalan Industrial Zone, Lahat.",c:[],w:""},
{n:"Herbal Land Mfg",l:"Perak",d:"MOH-registered herbal manufacturer in Menglembu Industrial Park.",c:[],w:""},
{n:"Wan Yeen",l:"Perak",d:"Contract manufacturer for herbal preparations, health food, and nutritional supplements.",c:[],w:"wyherbs.com"},
{n:"B2B Supplement",l:"Perak",d:"OEM/private label food supplement manufacturer helping local founders launch brands with low barrier.",c:[],w:"b2bsupplement.com"}
]},
{s:"3",g:"Certified specialists \u2014 Halal / GMP focus",cs:[
{n:"Unison Nutraceuticals",l:"Melaka",d:"PIC/s cGMP certified. OTC medicines, complementary medicine, health supplements, food supplements. One of few Malaysian CDMOs with PIC/s.",c:["GMP","PIC/s cGMP"],w:"unisonpharm.com"},
{n:"Duopharma Biotech",l:"Selangor",d:"First pharma manufacturer to receive Halal Malaysia certification for prescription medicines (2017). Bursa-listed.",c:["Halal"],w:"duopharmabiotech.com"},
{n:"MM Cosmetic",l:"",d:"Premium OEM gummy and capsule manufacturer. Customizable vitamin gummies, capsules, softgels for private label.",c:["GMP"],w:"mmcosmeticgmp.com"},
{n:"Foroem Phytonutrical",l:"",d:"Halal health supplement production under strict JAKIM guidelines. Capsules, powders, functional foods.",c:["Halal"],w:"foroem.com"},
{n:"HAX OEM",l:"",d:"OEM factory, 10+ years. Health supplements and body care products. Halal-certified.",c:["Halal"],w:"haxoem.com"},
{n:"My-Fitwell",l:"",d:"OEM for health food and functional beverages. Custom-formulated drinks, powders, sachets.",c:["Halal","HACCP"],w:"my-fitwell.com"},
{n:"D&O Nutra",l:"",d:"Halal-certified supplement manufacturer for private label brands.",c:["Halal"],w:"donutra.com"},
{n:"Genol Foods",l:"",d:"Halal OEM est. 2015. Health food powders with patented ingredients.",c:["Halal"],w:"genol.com.my"},
{n:"Excellent Foodtech",l:"",d:"Halal beverage manufacturer. Bottled bird\u2019s nest drinks, collagen drinks, fish scale collagen.",c:["Halal"],w:"excellentfoodtech.com"},
{n:"Sacha Inchi Marketing",l:"",d:"cGMP softgel manufacturer. High-quality soft gelatin capsules.",c:["GMP"],w:"sachainchimarketing.com"},
{n:"Protech Health Sci",l:"",d:"OEM collagen manufacturer, 20+ years. Collagen drinks, powder, capsules.",c:[],w:"protechhs.com"},
{n:"White Heron Pharma",l:"",d:"Multi-dosage: hard-shell capsules, soft-gels, tablets, powder, granules.",c:[],w:"whiteheron.com.my"},
{n:"Holista Biotech",l:"",d:"Collagen manufacturer.",c:[],w:""}
]},
{s:"3",g:"Other OEM / generalist",cs:[
{n:"Wen Ken Group",l:"SG/MY",d:"80+ year heritage. Three Legs Brand Cooling Water, balms, liniments, modern supplements. 15+ countries, 1,000+ staff.",c:[],w:"wenken.com",x:"4_branded_products"},
{n:"Genesis Nutraceuticals",l:"",d:"Supplement manufacturer since 2012. Science-backed health products.",c:[],w:"genesisnutraceuticals.com.my",x:"4_branded_products"},
{n:"Excel Herbal (est.1975)",l:"",d:"One-stop OEM nutraceutical and herbal manufacturer. One of the longest-operating in Malaysia.",c:[],w:"excelherbal.com"},
{n:"Era Herbal",l:"",d:"Herbal medicine manufacturer. Traditional formulations in modern dosage forms.",c:[],w:"eraherbal.com",x:"4_branded_products"},
{n:"ECOLITE",l:"",d:"Early bird\u2019s nest manufacturer. OEM for domestic and international brands.",c:[],w:"ecolite.com.my",x:"4_branded_products"},
{n:"Esprit Care",l:"",d:"OEM/ODM functional food manufacturer with R&D and formulation.",c:[],w:"espritcare.com"},
{n:"NUTRIGNOMIX",l:"",d:"Postbiotic OEM. 20+ years R&D in gut health and postbiotic formulations.",c:[],w:"nutrignomix.com"},
{n:"UNO Nutrition",l:"",d:"Contract manufacturing: nutrition supplements, meal replacements, protein beverages.",c:[],w:"unonutrition.com"},
{n:"Sirio Pharma",l:"Thailand",d:"China-based global CDMO. USD 40M facility in Chonburi for SEA gummy/softgel production.",c:["GMP"],w:"siriopharm.com"},
{n:"ITS Nutriscience",l:"Selangor",d:"Ingredient supplier and OEM. Formulation support, raw material sourcing.",c:[],w:"its-fpc.com",x:"2_extraction_ingredients"},
{n:"Bio Science Marketing",l:"",d:"OEM/ODM GMP factory. Powder, sachet, capsule, tablet, soft gel.",c:["GMP"],w:""},
{n:"DS Pharma Herbs",l:"",d:"NPRA-registered natural product manufacturer. Own herbal brands.",c:["NPRA"],w:"",x:"4_branded_products"},
{n:"HBT Co",l:"",d:"One-stop OEM for health supplements, health food, powdered supplement beverages.",c:[],w:"hbt.co.com"},
{n:"Masha Group",l:"",d:"Premium OEM/ODM capsule manufacturer. State-of-the-art facilities.",c:[],w:"masha.com.my"},
{n:"Bionutry",l:"",d:"Health product solutions: production, advisory, services.",c:[],w:"bionutry.com"},
{n:"Bio Life Neutraceuticals",l:"",d:"OEM/ODM for pharmaceutical and nutraceutical products.",c:[],w:""},
{n:"OEM Malaysia",l:"",d:"OEM for private label dietary supplements: men\u2019s health, women\u2019s health, slimming, general wellness.",c:[],w:"oemmalaysia.com"},
{n:"Nutri Action",l:"",d:"Supplementary and functional food products manufacturer.",c:[],w:"nutriaction.com.my"},
{n:"Natural Neutraceuticals",l:"",d:"Dietary supplements and functional products.",c:[],w:""},
{n:"SD Guthrie (Beyond)",l:"",d:"Health and wellness manufacturing. Dietary supplements from palm-based ingredients.",c:[],w:""}
]},
{s:"4",g:"Heritage / established brands",cs:[
{n:"DXN Holdings",l:"Kedah",d:"Ganoderma empire. Products: Lingzhi Coffee, Spirulina tablets, Cordyceps capsules, RG/GL extracts, personal care. 20M+ distributors. Bursa-listed (May 2023). Direct-selling model.",c:["GMP","Halal","ISO","Bursa-listed"],w:"dxn2u.com",x:"1_raw_materials"},
{n:"Hai-O",l:"",d:"First traditional healthcare company on Bursa (1996). Herbal medicines, health supplements, TCM, wellness products. Retail + direct selling.",c:[],w:"sgglobal.com.my",x:"3_cdmo_manufacturing"},
{n:"VitaHealth",l:"",d:"Premium supplements: vitamins, minerals, joint care, eye care, liver care, children\u2019s range. Halal-certified. Strong pharmacy distribution.",c:["Halal"],w:"vitahealth.com.my",x:"5_distribution_retail"},
{n:"Vitagen",l:"",d:"Probiotics company. Products: Vitagen cultured milk, Enfa probiotic drinks. Halal functional health beverages. Household brand.",c:["Halal"],w:"",x:"3_cdmo_manufacturing"},
{n:"21st Century",l:"Selangor",d:"Consumer supplement brand. Vitamins, minerals, general health supplements. Affordable mass-market, pharmacy channel.",c:[],w:"21stcentury.com.my"},
{n:"Kinohimitsu",l:"",d:"ASEAN\u2019s No.1 Collagen Brand. Collagen drinks, bird\u2019s nest collagen, beauty supplements. SGS-certified drug-free, hormone-free.",c:["SGS"],w:"my.kinohimitsu.com"},
{n:"Recogen",l:"",d:"Joint health specialist. Halal collagen peptide supplements for knee pain relief. Aging/mobility segment.",c:["Halal"],w:"recogen.com.my"},
{n:"BioGaia Malaysia",l:"",d:"Swedish-origin probiotic brand. Patented human-strain probiotic drops, tablets, capsules for gut, immune, oral health.",c:[],w:"biogaia.com.my"},
{n:"LAC Malaysia",l:"",d:"Probiotics brand (formerly GNC sub-brand). Targeted probiotic formulations by lifestyle and life stage.",c:[],w:"lacworldwide.com.my"},
{n:"FINE Japan",l:"",d:"Japanese health & beauty brand. Collagen drinks, hyaluronic acid, green tea extract products.",c:[],w:"finemalaysia.com"}
]},
{s:"4",g:"Tongkat Ali & botanical brands",cs:[
{n:"AKARALI",l:"",d:"Premium Tongkat Ali brand. Clinically tested hot water standardized extract. 26 clinical trials. Partners with Biotropics for Physta\u00ae ingredient.",c:[],w:"akarali.com",x:"2_extraction_ingredients"},
{n:"NuPrep (Biotropics)",l:"Selangor",d:"Biotropics\u2019 consumer brand. Physta\u00ae Tongkat Ali capsules and sachets for men\u2019s and women\u2019s health. Pharmacy and online.",c:["Halal"],w:"nuprep.com"},
{n:"Ayu Flores",l:"",d:"Largest Tongkat Ali & Kacip Fatimah specialty store. Capsules, raw powder, root chips, liquid extracts.",c:[],w:"ayuflores.com",x:"5_distribution_retail"},
{n:"Biobay",l:"",d:"Palm-derived supplement brand. Tocotrienol Plus, mixed carotene supplements, healthcare products.",c:[],w:"biobay.com.my"}
]},
{s:"4",g:"Bird\u2019s nest brands",cs:[
{n:"G Nest",l:"",d:"Award-winning bird\u2019s nest brand. Premium bottled drinks, dried bird\u2019s nest.",c:[],w:"gnest.my"},
{n:"Yu Nest",l:"Pahang",d:"Bird\u2019s nest drink supplier est. 2010. Ready-to-drink beverages.",c:[],w:"yunest.com.my"},
{n:"TCK BON",l:"Penang",d:"Est. 2009. Professional health & nutritional supplements. Retail stores in Penang.",c:[],w:"bon.com.my",x:"5_distribution_retail"}
]},
{s:"4",g:"New-wave D2C / digital-first",cs:[
{n:"Lumi Beauty",l:"Selangor",d:"NMN beauty-from-within brand. NMN capsules, collagen drinks. Digital-first via Shopee, Lazada, TikTok Shop.",c:[],w:""},
{n:"Youvit",l:"ID/MY",d:"Gummy vitamin brand. Unilever-invested. 7-day packs (~USD 1.20), multivitamins, beauty gummies. Digital-first, convenience store model.",c:[],w:"youvit.com"},
{n:"Envisionary Life",l:"KL",d:"US-origin NMN brand. Revive, Body Vitality, NMN supplements. LNDT absorption technology. Bangsar South office.",c:[],w:""},
{n:"AvantHealth",l:"Penang",d:"Health supplements and skincare. D2C focus.",c:[],w:"avant.health"},
{n:"AG Nutrition",l:"Selangor",d:"Health supplement brand in PJ.",c:[],w:""},
{n:"Manuka Biotech",l:"Johor",d:"Omega-3 manufacturer in Kulai. Fish oil capsules, omega-3 supplements.",c:[],w:"manukabiotech.com"}
]},
{s:"4",g:"Other branded",cs:[
{n:"Cleavia Group",l:"Selangor",d:"Nutraceutical startup.",c:[],w:""},
{n:"Nutrae",l:"Johor",d:"Nutraceutical company in Johor Bahru.",c:[],w:""},
{n:"Primus Wellness",l:"KL",d:"Moringa-based supplements. Capsules, lotion, body wash. KKM + JAKIM Halal certified.",c:["KKM","JAKIM Halal"],w:""},
{n:"DS Pharma Herbs",l:"",d:"NPRA-registered natural product manufacturer with own herbal brands.",c:["NPRA"],w:""}
]},
{s:"5",g:"Pharmacy chains",cs:[
{n:"Caring Pharmacy",l:"National",d:"Largest pharmacy chain in Malaysia. Bursa-listed. Key supplement distribution channel. Stocks major local and international nutraceutical brands.",c:["Bursa-listed"],w:"caring2u.com"},
{n:"Watsons",l:"National",d:"Health & beauty retail (A.S. Watson Group). Major supplement retailer with nationwide stores and strong online channel.",c:[],w:"watsons.com.my"},
{n:"Guardian",l:"National",d:"Pharmacy and health retail (Dairy Farm Group). Supplement retail alongside pharmaceutical dispensing.",c:[],w:"guardian.com.my"}
]},
{s:"5",g:"Specialty distributors",cs:[
{n:"LAC Nutrition For Life",l:"KL",d:"Rebranded from GNC Malaysia. Premium supplements, sports nutrition, weight management. Retail stores in major malls.",c:[],w:""},
{n:"InterMed",l:"",d:"Food & Nutraceuticals Division: distribution of raw materials and active ingredients to manufacturers.",c:[],w:"intermed.com.my"},
{n:"S&S Foods",l:"",d:"Botanical extract distributor. Partnership with Skyherbs for ingredient supply.",c:[],w:"ssfoods.com.my"},
{n:"Unimed",l:"Penang",d:"Pharmaceutical company importing, marketing, distributing pharma and nutraceutical products.",c:[],w:"unimed.com.my"},
{n:"Urbax Health Science",l:"Perak",d:"Nutritional supplement distributor. Founded 2020 by industry professionals.",c:[],w:""},
{n:"Vortexin",l:"",d:"Est. 2007. Sales, marketing, distribution of premium healthcare supplements.",c:[],w:"vortexin.com.my"}
]},
{s:"6",g:"",cs:[
{n:"NPRA",l:"Selangor",d:"National Pharmaceutical Regulatory Agency under MOH. Health supplement registration (MAL number). PIC/S member enabling exports to EU, Canada, Australia. Approval: 116\u2013140 working days. Governs claims classification.",c:["PIC/S member"],w:"npra.gov.my"},
{n:"JAKIM",l:"Putrajaya",d:"Department of Islamic Development Malaysia. Sole domestic halal certifier. Malaysia ranks #1 on Global Islamic Economy Indicator (GIEI). Recognized across OIC member countries\u2014access to 2B+ Muslim consumers.",c:["GIEI #1"],w:"halal.gov.my"},
{n:"SIRIM",l:"Selangor",d:"National standards and quality organization. Manages MS2409 (Tongkat Ali standard). Testing, calibration, certification for nutraceutical manufacturers.",c:[],w:"sirim.my"},
{n:"FRIM",l:"Selangor",d:"Forest Research Institute Malaysia. Botanical R&D, Tongkat Ali standardization, HPLC fingerprinting. Collaborates with Rainforest Herbs and others on quality benchmarks.",c:[],w:"frim.gov.my"}
]}
];
