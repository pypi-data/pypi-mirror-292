from ._integration import OdooIntegration


class ContactModel(OdooIntegration):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_partner_by_id(self, partner_id):
        response = self.read("res.partner", [partner_id])
        return response


    def get_partner_id_by_name(self, partner_name):
        response = self.search("res.partner", [[["name", "=", partner_name]]])
        if response:
            return response[0]
        raise Exception(f"Partner '{partner_name}' not found")
    

    def create_partner(
        self,
        name,
        street,
        city,
        state_id,
        country_id,
        zip_code,
        nif,
        contact_type,
        anf_code,
        pharmacy_name,
        owner_name,
        phone,
        mobile,
        email,
        list_category_id,
        list_crm_tag_id,
        vendor_user_id,
        reference,
        language="pt_PT",
        is_company=True,
        company_type="company",
    ):
        # state_id = self.get_state_id_by_name(state)
        # country_id = self.get_country_id_by_code(country)
        # list_category_id = []
        # for category_name in list_category_name:
        #      list_category_id.append(self.get_category_id_by_name(category_name))

        # list_crm_tag_id = []
        # for crm_tag_name in list_crm_tag_name:
        #     list_crm_tag_id.append(self.get_crm_tag_id_by_name(crm_tag_name))

        # vendor_user_id = self.get_user_id_by_name(vendor_user_name)

        partner_data = {
            "name": name,
            "street": street,
            "city": city,
            "state_id": state_id,  # "Lisboa", # aqui deve-se buscar o state_id pelo nome do estado
            "country_id": country_id,  # "Portugal", # aqui deve-se buscar o country_id pelo nome do país
            "zip": zip_code,
            "vat": nif,  # NIF
            "x_studio_tipo_de_contacto_1": contact_type,  # Tipo de Contacto
            "x_studio_cdigo_anf_1": anf_code,  # apenas para tipo farmácia
            "x_studio_nome_da_farmcia_1": pharmacy_name,  # apenas para tipo farmácia
            "x_studio_nome_do_proprietrio_1": owner_name,  # apenas para tipo farmácia
            "phone": phone,
            "mobile": mobile,
            "email": email,
            "lang": language,  # idioma
            "category_id": list_category_id,  # Etiquetas / labels - models: res.partner.category - fields: name, active (booleean), parent_id (categoria pai), display_name
            "x_studio_etiquetas_crm": list_crm_tag_id,  # model: crm.tag - fields: name, id, color
            "user_id": vendor_user_id,  # models: res.users - fields: name
            "ref": reference,  # Referência
            "is_company": is_company,  # se é empresa ou não
            "company_type": company_type,  # tipo de empresa
        }
        response = self.create("res.partner", [partner_data])
        return response