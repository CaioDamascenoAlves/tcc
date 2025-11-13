"""
Timeline component customizado com largura total.

Baseado em streamlit-timeline, mas com width: 100%.
"""

import json
import streamlit as st
import streamlit.components.v1 as components


def timeline_fullwidth(data, height=800, use_container_width=True):
    """
    Cria um componente de timeline com largura total.

    Esta é uma versão modificada do streamlit-timeline que usa width: 100%
    ao invés do hardcoded 95%.

    Parameters
    ----------
    data: str or dict
        String ou dict no formato JSON da timeline: https://timeline.knightlab.com/docs/json-format.html
    height: int or None
        Altura da timeline em px

    Returns
    -------
    static_component: Boolean
        Retorna um componente estático com a timeline
    """

    # Se for string, converter para JSON
    if isinstance(data, str):
        data = json.loads(data)

    # JSON para string
    json_text = json.dumps(data)

    # Carregar JSON
    source_param = 'timeline_json'
    source_block = f'var {source_param} = {json_text};'

    # Carregar CSS + JS do CDN do Knight Lab
    cdn_path = 'https://cdn.knightlab.com/libs/timeline3/latest'
    css_block = f'<link title="timeline-styles" rel="stylesheet" href="{cdn_path}/css/timeline.css">'
    js_block  = f'<script src="{cdn_path}/js/timeline.js"></script>'

    # HTML customizado com width: 100% (ao invés de 95%)
    htmlcode = css_block + '''
    ''' + js_block + '''

        <div id='timeline-embed' style="width: 100%; height: '''+str(height)+'''px"></div>

        <script type="text/javascript">
            var additionalOptions = {
                start_at_end: false,
                is_embed: true,
            }
            '''+source_block+'''
            timeline = new TL.Timeline('timeline-embed', '''+source_param+''', additionalOptions);
        </script>'''

    # Retornar HTML renderizado
    # Tentar usar st.container com use_container_width para forçar largura total
    if use_container_width:
        # Usar container do Streamlit para controlar largura
        with st.container():
            # Adicionar CSS adicional no próprio Streamlit
            st.markdown("""
                <style>
                /* Forçar iframe do componente a usar largura total */
                iframe {
                    width: 100% !important;
                }
                </style>
            """, unsafe_allow_html=True)

            static_component = components.html(
                htmlcode,
                height=height,
                scrolling=False
            )
    else:
        static_component = components.html(
            htmlcode,
            height=height,
            scrolling=False
        )

    return static_component
