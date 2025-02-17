import streamlit as st
from rdflib import Graph, Namespace, RDF, RDFS, Literal

def main():
    st.set_page_config(page_title="Tourism Data", layout="centered")
    
    st.markdown(
        """
        <style>
        /* กำหนด style แบบง่าย ๆ */
        .title {
            font-size: 2em;
            color: #2E86C1;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0.5em;
        }
        .subtitle {
            font-size: 1.2em;
            color: #555555;
            text-align: center;
            margin-bottom: 1em;
        }
        .divider {
            height: 2px;
            background-color: #cccccc;
            margin: 1em 0;
        }
        .result-title {
            font-weight: bold;
            font-size: 1.1em;
            color: #1B9C85;
        }
        .result-value {
            margin-bottom: 0.5em;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="title">ค้นหาข้อมูลจังหวัด</div>', unsafe_allow_html=True)

    owl_file = "mytourism.owl" 
    g = Graph()
    g.parse(owl_file)

    MYT = Namespace("http://www.my_ontology.edu/mytourism#")
    g.bind("myt", MYT)


    query_possible_values = """
    SELECT DISTINCT ?val
    WHERE {
      ?prov a myt:ThaiProvince .
      {
        ?prov myt:hasNameOfProvince ?val .
        FILTER(lang(?val) = "th" || lang(?val) = "en")
      }
      UNION
      {
        ?prov myt:hasTraditionalNameOfProvince ?val .
        FILTER(lang(?val) = "th" || lang(?val) = "en")
      }
      UNION
      {
        ?prov myt:hasTree ?val .
        FILTER(lang(?val) = "th" || lang(?val) = "en")
      }
      UNION
      {
        ?prov myt:hasFlower ?val .
        FILTER(lang(?val) = "th" || lang(?val) = "en")
      }
    }
    ORDER BY ?val
    """

    results_list = g.query(query_possible_values)
    possible_values = [str(row.val) for row in results_list]

    selected_value = st.selectbox(
        "พิมพ์/เลือกข้อมูล (ชื่อจังหวัด, ชื่อท้องถิ่น, ต้นไม้, ดอกไม้) ได้ทั้งไทยหรืออังกฤษ",
        options=[""] + possible_values,
        help="หากไม่ทราบ exact value สามารถลองพิมพ์บางส่วนเพื่อค้นหา"
    )

    display_lang = st.radio("เลือกภาษาสำหรับการแสดงผล", ["Thai", "English"], horizontal=True)
    selected_lang_code = "th" if display_lang == "Thai" else "en"

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if selected_value != "":
        query_info = f"""
        SELECT DISTINCT ?provName ?tradName ?tree ?flower ?motto ?seal ?lat ?long
        WHERE {{
            ?prov a myt:ThaiProvince .

            {{
                ?prov myt:hasNameOfProvince ?x .
                FILTER(str(?x) = "{selected_value}")
            }} UNION {{
                ?prov myt:hasTraditionalNameOfProvince ?x .
                FILTER(str(?x) = "{selected_value}")
            }} UNION {{
                ?prov myt:hasTree ?x .
                FILTER(str(?x) = "{selected_value}")
            }} UNION {{
                ?prov myt:hasFlower ?x .
                FILTER(str(?x) = "{selected_value}")
            }}

            OPTIONAL {{ ?prov myt:hasNameOfProvince ?provName . FILTER(lang(?provName) = "{selected_lang_code}") }}
            OPTIONAL {{ ?prov myt:hasTraditionalNameOfProvince ?tradName . FILTER(lang(?tradName) = "{selected_lang_code}") }}
            OPTIONAL {{ ?prov myt:hasTree ?tree . FILTER(lang(?tree) = "{selected_lang_code}") }}
            OPTIONAL {{ ?prov myt:hasFlower ?flower . FILTER(lang(?flower) = "{selected_lang_code}") }}
            OPTIONAL {{ ?prov myt:hasMotto ?motto . FILTER(lang(?motto) = "{selected_lang_code}") }}
            OPTIONAL {{ ?prov myt:hasSeal ?seal. }}
            OPTIONAL {{ ?prov myt:hasLatitudeOfProvince ?lat. }}
            OPTIONAL {{ ?prov myt:hasLongitudeOfProvince ?long. }}
        }}
        """

        results_info = g.query(query_info)

        if len(results_info) == 0:
            st.error("ไม่พบข้อมูลที่สอดคล้องกับ: " + selected_value)
        else:
            st.success(f"ผลลัพธ์ที่ค้นพบ ({len(results_info)} รายการ) :")
            for row in results_info:
                name_out = row.provName if row.provName else "-"
                trad_out = row.tradName if row.tradName else "-"
                tree_out = row.tree if row.tree else "-"
                flower_out = row.flower if row.flower else "-"
                motto_out = row.motto if row.motto else "-"
                seal_out = row.seal if row.seal else "-"
                lat_out = row.lat if row.lat else "-"
                long_out = row.long if row.long else "-"

                st.markdown(
                    f'<div class="result-title">-- ข้อมูลจังหวัด <span style="font-size: 25px">{name_out}</span> --</div>',
                    unsafe_allow_html=True
                )
                st.markdown(f'<div class="result-value"><b>🌆ชื่อจังหวัด:</b> {name_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>🦹ชื่อท้องถิ่น:</b> {trad_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>🌲ต้นไม้ประจำจังหวัด:</b> {tree_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>🪷ดอกไม้ประจำจังหวัด:</b> {flower_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>💬คำขวัญจังหวัด:</b> {motto_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>🦄ตราสัญลักษณ์:</b> {seal_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>✖️Latitude:</b> {lat_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>✝️Longitude:</b> {long_out}</div>', unsafe_allow_html=True)
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
