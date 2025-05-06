import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from PIL import Image
import requests
from io import BytesIO
import hashlib
import re
from bs4 import BeautifulSoup



# Configuração inicial
st.set_page_config(page_title="📊 Meta Ads Analyzer Pro", page_icon="📊", layout="wide")

# Função auxiliar para conversão segura de valores numéricos
def safe_float(value, default=0.0):
    try:
        return float(value) if value not in [None, ''] else default
    except (TypeError, ValueError):
        return default

def safe_int(value, default=0):
    try:
        return int(float(value)) if value not in [None, ''] else default
    except (TypeError, ValueError):
        return default

# ==============================================
# SISTEMA AVANÇADO DE RECOMENDAÇÕES (NOVO)
# ==============================================

def calculate_industry_benchmark(objective):
    """Retorna benchmarks baseados no objetivo da campanha"""
    benchmarks = {
        'CONVERSIONS': 25.00,
        'LEAD_GENERATION': 15.00,
        'LINK_CLICKS': 1.20,
        'REACH': 5.00,
        'BRAND_AWARENESS': 10.00,
        'VIDEO_VIEWS': 0.50
    }
    return benchmarks.get(objective, 20.00)

def analyze_creative_elements(creative_data):
    """Analisa elementos criativos específicos"""
    recommendations = []
    
    if 'primary_text' in creative_data:
        text = creative_data['primary_text']
        word_count = len(text.split())
        
        if word_count > 125:
            recommendations.append({
                'title': 'Otimização de Texto',
                'severity': 'medium',
                'diagnosis': f"Texto muito longo ({word_count} palavras), ideal é <125 caracteres",
                'actions': [
                    "Reduzir texto em 30-40% mantendo a mensagem principal",
                    "Testar versão com bullet points",
                    "Mover detalhes para a descrição ou website"
                ],
                'expected_impact': "Aumento de 10-20% no CTR",
                'timeframe': "Imediato"
            })
    
    if 'cta' not in creative_data or not creative_data['cta']:
        recommendations.append({
            'title': 'Adicionar Call-to-Action',
            'severity': 'high',
            'diagnosis': "Nenhum CTA específico identificado no criativo",
            'actions': [
                "Adicionar CTA claro como 'Compre Agora' ou 'Saiba Mais'",
                "Posicionar CTA nos primeiros 3 segundos (vídeo) ou acima do scroll (imagem)",
                "Testar 2-3 variações de CTA"
            ],
            'expected_impact': "Aumento de 15-25% nas conversões",
            'timeframe': "1-3 dias"
        })
    
    return recommendations

# ==============================================
# CONFIGURAÇÃO DA API DO META
# ==============================================
def generate_ai_optimization_recommendations(ad_details, insights, temporal_data, demographics):
    """Gera recomendações de otimização baseadas em IA analisando todas as métricas disponíveis"""
    recommendations = []
    
    # 1. Análise de CTR
    ctr = safe_float(insights.get('ctr', 0)) * 100
    avg_ctr_benchmark = 1.5
    
    if ctr < avg_ctr_benchmark * 0.7:
        diagnosis = []
        if safe_float(insights.get('frequency', 0)) > 3:
            diagnosis.append(f"Frequência alta ({insights.get('frequency', 0):.1f}x) indicando possível fadiga criativa")
        
        if safe_float(insights.get('cpm', 0)) > avg_ctr_benchmark * 1.3:
            diagnosis.append(f"CPM elevado (R${insights.get('cpm', 0):.2f}) sugerindo público competitivo")
        
        creative_type = ad_details.get('ad_type', 'desconhecido')
        recommendations.append({
            'title': 'Otimização de CTR Urgente',
            'severity': 'high',
            'diagnosis': f"CTR muito baixo ({ctr:.2f}% vs benchmark {avg_ctr_benchmark}%). Possíveis causas: {', '.join(diagnosis) if diagnosis else 'criativo ou segmentação inadequados'}",
            'actions': [
                f"Testar 3 novos criativos de {creative_type} com abordagens diferentes",
                "Reduzir texto principal para menos de 125 caracteres" if creative_type in ['image', 'carousel'] else "Adicionar legendas claras" if creative_type == 'video' else "Simplificar mensagem",
                f"Ajustar público-alvo (atual: {ad_details.get('targeting', 'não especificado')})",
                "Implementar rodízio de criativos a cada 3 dias"
            ],
            'expected_impact': "Aumento de 30-50% no CTR",
            'timeframe': "3-5 dias para ver resultados"
        })
    
    # 2. Análise de Custo por Conversão
    cost_per_conv = safe_float(insights.get('cost_per_conversion', 0))
    conv_rate = safe_float(insights.get('conversion_rate', 0))
    
    if cost_per_conv > 0 and conv_rate > 0:
        benchmark_cpa = calculate_industry_benchmark(ad_details['campaign_objective'])
        if cost_per_conv > benchmark_cpa * 1.2:
            recommendations.append({
                'title': 'Redução de Custo por Conversão',
                'severity': 'high',
                'diagnosis': f"Custo por conversão (R${cost_per_conv:.2f}) está {((cost_per_conv/benchmark_cpa)-1)*100:.0f}% acima do benchmark ({benchmark_cpa:.2f})",
                'actions': [
                    "Otimizar página de destino para melhorar taxa de conversão",
                    "Testar novos CTAs no anúncio e na landing page",
                    f"Ajustar bid strategy (atual: {ad_details.get('bid_strategy', 'não especificado')})",
                    "Segmentar público semelhante a converters (lookalike)"
                ],
                'expected_impact': "Redução de 20-35% no CPA",
                'timeframe': "1-2 semanas para otimização completa"
            })
    
    # 3. Análise de Frequência e Saturação
    freq = safe_float(insights.get('frequency', 0))
    if freq > 3.5:
        rec = {
            'title': 'Rotação de Criativos Necessária',
            'severity': 'medium',
            'diagnosis': f"Frequência alta ({freq:.1f}x) indica saturação do público",
            'actions': [
                "Pausar este anúncio por 7 dias",
                "Criar 2-3 variações com novos criativos",
                "Expandir público-alvo em 15-20%"
            ],
            'expected_impact': "Melhoria de 15-25% nas taxas de engajamento",
            'timeframe': "Imediato"
        }
        
        if ad_details.get('ad_type') == 'video':
            rec['actions'].extend([
                "Testar versão resumida do vídeo (15-30s)",
                "Adicionar hook nos primeiros 3 segundos"
            ])
        recommendations.append(rec)
    
    # 4. Análise Demográfica
    if demographics:
        demo_df = pd.DataFrame([{
            'age': d.get('age', 'N/A'),
            'gender': d.get('gender', 'N/A'),
            'impressions': safe_int(d.get('impressions', 0)),
            'spend': safe_float(d.get('spend', 0)),
            'conversions': safe_int(d.get('conversions', 0))
        } for d in demographics if 'age' in d])
        
        if not demo_df.empty:
            demo_df['cpa'] = demo_df['spend'] / demo_df['conversions'].replace(0, 1)
            worst_performing = demo_df.sort_values('cpa', ascending=False).iloc[0]
            
            if worst_performing['cpa'] > cost_per_conv * 1.5:
                recommendations.append({
                    'title': 'Ajuste de Segmentação Demográfica',
                    'severity': 'medium',
                    'diagnosis': f"Segmento {worst_performing['age']} {worst_performing['gender']} tem CPA {worst_performing['cpa']:.2f} ({(worst_performing['cpa']/cost_per_conv-1)*100:.0f}% acima da média)",
                    'actions': [
                        f"Reduzir orçamento para {worst_performing['age']} {worst_performing['gender']} em 30%",
                        "Criar anúncio específico para este segmento",
                        "Testar mensagens personalizadas para este grupo"
                    ],
                    'expected_impact': "Redução de 15-20% no CPA geral",
                    'timeframe': "5-7 dias"
                })
    
    # 5. Análise Temporal
    if temporal_data is not None:
        temporal_data['day_of_week'] = temporal_data['date_start'].dt.day_name()
        temporal_data['hour'] = temporal_data['date_start'].dt.hour
        
        best_day = temporal_data.groupby('day_of_week')['conversions'].sum().idxmax()
        best_hour = temporal_data.groupby('hour')['conversions'].sum().idxmax()
        
        recommendations.append({
            'title': 'Otimização de Agendamento',
            'severity': 'low',
            'diagnosis': f"Melhor desempenho às {best_hour}h nas {best_day}s",
            'actions': [
                f"Concentrar 40% do orçamento nas {best_day}s",
                f"Aumentar bids em 15% entre {best_hour-1}-{best_hour+1}h",
                "Reduzir bids em 20% nos horários de pior desempenho"
            ],
            'expected_impact': "Aumento de 10-15% na eficiência do orçamento",
            'timeframe': "Próxima semana"
        })
    
    # 6. Análise de Creativos (se disponível)
    if 'creative' in ad_details:
        creative_analysis = analyze_creative_elements(ad_details['creative'])
        if creative_analysis:
            recommendations.extend(creative_analysis)
    
    # Prioriza recomendações por severidade e impacto
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda x: priority_order[x['severity']])
    
    return recommendations

def init_facebook_api():
    """Inicializa a conexão com a API do Meta com credenciais do usuário"""
    st.sidebar.title("🔐 Configuração da API do Meta")
    
    with st.sidebar.expander("🔑 Inserir Credenciais", expanded=True):
        app_id = st.text_input("App ID", help="ID do aplicativo Facebook")
        app_secret = st.text_input("App Secret", type="password", help="Chave secreta do aplicativo")
        access_token = st.text_input("Access Token", type="password", help="Token de acesso de longo prazo")
        ad_account_id = st.text_input("Ad Account ID", help="ID da conta de anúncios (sem 'act_')")
    
    if not all([app_id, app_secret, access_token, ad_account_id]):
        st.warning("Por favor, preencha todas as credenciais na barra lateral")
        return None
    
    try:
        FacebookAdsApi.init(app_id, app_secret, access_token)
        return AdAccount(f"act_{ad_account_id}")
    except Exception as e:
        st.error(f"Erro ao conectar à API do Meta: {str(e)}")
        return None

# ==============================================
# FUNÇÕES PARA EXTRAÇÃO DE DADOS REAIS (API)
# ==============================================

def get_campaigns(ad_account):
    """Obtém campanhas da conta de anúncio formatadas como dicionários"""
    try:
        fields = ['id', 'name', 'objective', 'status', 'start_time', 'stop_time', 'buying_type']
        params = {'limit': 200}
        
        campaigns = ad_account.get_campaigns(fields=fields, params=params)
        
        campaigns_data = []
        for campaign in campaigns:
            campaigns_data.append({
                'id': campaign.get('id'),
                'name': campaign.get('name', 'Sem Nome'),
                'objective': campaign.get('objective', 'N/A'),
                'status': campaign.get('status', 'N/A'),
                'start_time': campaign.get('start_time', 'N/A'),
                'stop_time': campaign.get('stop_time', 'N/A'),
                'buying_type': campaign.get('buying_type', 'N/A')
            })
        
        return campaigns_data
    except Exception as e:
        st.error(f"Erro ao obter campanhas: {str(e)}")
        return []

def get_adsets(campaign_id):
    """Obtém conjuntos de anúncios de uma campanha"""
    try:
        fields = [
            'id', 'name', 'daily_budget', 'lifetime_budget', 
            'start_time', 'end_time', 'optimization_goal',
            'billing_event', 'targeting', 'bid_strategy'
        ]
        params = {'limit': 100}
        campaign = Campaign(campaign_id)
        adsets = campaign.get_ad_sets(fields=fields, params=params)
        
        adsets_data = []
        for adset in adsets:
            adsets_data.append({
                'id': adset.get('id'),
                'name': adset.get('name', 'Sem Nome'),
                'daily_budget': safe_float(adset.get('daily_budget', 0)),
                'lifetime_budget': safe_float(adset.get('lifetime_budget', 0)),
                'start_time': adset.get('start_time', 'N/A'),
                'end_time': adset.get('end_time', 'N/A'),
                'optimization_goal': adset.get('optimization_goal', 'N/A'),
                'billing_event': adset.get('billing_event', 'N/A'),
                'bid_strategy': adset.get('bid_strategy', 'N/A')
            })
        
        return adsets_data
    except Exception as e:
        st.error(f"Erro ao obter conjuntos de anúncios: {str(e)}")
        return []

def get_ads(adset_id):
    """Obtém anúncios de um conjunto"""
    try:
        fields = [
            'id', 'name', 'status', 'created_time', 
            'adset_id', 'creative', 'bid_amount',
            'conversion_domain', 'targeting'
        ]
        params = {'limit': 100}
        adset = AdSet(adset_id)
        ads = adset.get_ads(fields=fields, params=params)
        
        ads_data = []
        for ad in ads:
            ads_data.append({
                'id': ad.get('id'),
                'name': ad.get('name', 'Sem Nome'),
                'status': ad.get('status', 'N/A'),
                'created_time': ad.get('created_time', 'N/A'),
                'adset_id': ad.get('adset_id', 'N/A'),
                'bid_amount': safe_float(ad.get('bid_amount', 0)),
                'conversion_domain': ad.get('conversion_domain', 'N/A')
            })
        
        return ads_data
    except Exception as e:
        st.error(f"Erro ao obter anúncios: {str(e)}")
        return []

def get_ad_insights(ad_id, date_range='last_30d'):
    """Obtém métricas de desempenho do anúncio com mais detalhes"""
    try:
        fields = [
            'impressions', 'reach', 'frequency', 
            'spend', 'cpm', 'cpp', 'ctr', 'clicks',
            'conversions', 'actions', 'action_values',
            'cost_per_conversion', 'cost_per_action_type',
            'cost_per_unique_click', 'cost_per_unique_action_type',
            'unique_clicks', 'unique_actions',
            'quality_ranking', 'engagement_rate_ranking',
            'conversion_rate_ranking', 'video_p25_watched_actions',
            'video_p50_watched_actions', 'video_p75_watched_actions',
            'video_p95_watched_actions', 'video_p100_watched_actions',
            'video_avg_time_watched_actions'
        ]
        
        # Limite de 37 meses para o intervalo de datas
        max_months = 37
        
        if date_range == 'last_30d':
            since = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            until = datetime.now().strftime('%Y-%m-%d')
        elif date_range == 'last_7d':
            since = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            until = datetime.now().strftime('%Y-%m-%d')
        else:
            since, until = date_range.split('_to_')
            since_date = datetime.strptime(since, '%Y-%m-%d')
            until_date = datetime.strptime(until, '%Y-%m-%d')
            if (until_date - since_date).days > (max_months * 30):
                st.warning(f"O intervalo máximo permitido é de {max_months} meses. Ajustando automaticamente.")
                since = (until_date - timedelta(days=max_months*30)).strftime('%Y-%m-%d')
        
        params = {
            'time_range': {'since': since, 'until': until},
            'level': 'ad',
            'limit': 100
        }
        
        ad = Ad(ad_id)
        insights = ad.get_insights(fields=fields, params=params)
        
        if insights:
            # Processa ações específicas
            actions = insights[0].get('actions', [])
            action_data = {}
            for action in actions:
                action_type = action.get('action_type')
                value = safe_float(action.get('value', 0))
                action_data[f'action_{action_type}'] = value
            
            # Processa valores de ação
            action_values = insights[0].get('action_values', [])
            for action in action_values:
                action_type = action.get('action_type')
                value = safe_float(action.get('value', 0))
                action_data[f'action_value_{action_type}'] = value
            
            # Adiciona ao dicionário de insights
            insight_dict = {**insights[0], **action_data}
            return insight_dict
        
        return None
    except Exception as e:
        st.error(f"Erro ao obter insights do anúncio: {str(e)}")
        return None

def get_ad_demographics(ad_id, date_range='last_30d'):
    """Obtém dados demográficos detalhados com mais métricas"""
    try:
        fields = [
            'impressions', 'reach', 'frequency',
            'clicks', 'spend', 'conversions',
            'ctr', 'cpm', 'cpp', 
            'cost_per_conversion'
        ]
        
        # Breakdowns mais simples para garantir funcionamento
        breakdowns = ['age', 'gender']
        
        if date_range == 'last_30d':
            since = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            until = datetime.now().strftime('%Y-%m-%d')
        elif date_range == 'last_7d':
            since = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            until = datetime.now().strftime('%Y-%m-%d')
        else:
            since, until = date_range.split('_to_')

        params = {
            'time_range': {'since': since, 'until': until},
            'breakdowns': breakdowns,
            'level': 'ad'
        }
        
        ad = Ad(ad_id)
        insights = ad.get_insights(fields=fields, params=params)
        
        if not insights:
            return []

        processed_data = []
        for insight in insights:
            try:
                segment = {
                    'age': insight.get('age', 'N/A'),
                    'gender': insight.get('gender', 'N/A'),
                    'impressions': safe_int(insight.get('impressions', 0)),
                    'reach': safe_int(insight.get('reach', 0)),
                    'clicks': safe_int(insight.get('clicks', 0)),
                    'spend': safe_float(insight.get('spend', 0)),
                    'conversions': safe_int(insight.get('conversions', 0)),
                    'ctr': safe_float(insight.get('ctr', 0)) * 100,
                    'cpm': safe_float(insight.get('cpm', 0))
                }
                processed_data.append(segment)
            except Exception as e:
                st.warning(f"Erro ao processar insight: {str(e)}")
                continue
        
        return processed_data

    except Exception as e:
        st.error(f"Erro ao obter dados demográficos: {str(e)}")
        return []
    
def show_detailed_audience_analysis(demographics):
    """Mostra análise detalhada do público-alvo"""
    if not demographics:
        st.warning("Dados demográficos não disponíveis para este anúncio.")
        return
    
    st.markdown("### 👥 Análise Detalhada do Público")
    
    # Filtros para análise
    col1, col2 = st.columns(2)
    with col1:
        segment_type = st.selectbox(
            "Tipo de Segmento:",
            options=['demographic', 'geographic', 'device', 'placement'],
            index=0
        )
    
    with col2:
        metric = st.selectbox(
            "Métrica Principal:",
            options=['impressions', 'reach', 'clicks', 'conversions', 'ctr', 'cost_per_conversion'],
            index=3
        )
    
    # Filtrar dados pelo tipo de segmento selecionado
    segment_data = [d for d in demographics if d.get('segment_type') == segment_type]
    
    if not segment_data:
        st.warning(f"Nenhum dado disponível para o tipo de segmento {segment_type}")
        return
    
    # Criar DataFrame para análise
    df = pd.DataFrame(segment_data)
    
    # Visualização específica por tipo de segmento
    if segment_type == 'demographic':
        st.markdown("#### 📊 Distribuição por Idade e Gênero")
        
        # Pivot table para heatmap
        pivot_table = df.pivot_table(
            index='age', 
            columns='gender', 
            values=metric, 
            aggfunc='sum'
        ).fillna(0)
        
        fig = px.imshow(
            pivot_table,
            labels=dict(x="Gênero", y="Idade", color=metric),
            title=f"{metric.upper()} por Idade e Gênero",
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise de performance por segmento
        st.markdown("#### 🏆 Melhores Segmentos Demográficos")
        
        top_segments = df.groupby(['age', 'gender']).agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'spend': 'sum'
        }).reset_index()
        
        top_segments['ctr'] = (top_segments['clicks'] / top_segments['impressions']) * 100
        top_segments['cpa'] = top_segments['spend'] / top_segments['conversions']
        top_segments['conversion_rate'] = (top_segments['conversions'] / top_segments['clicks']) * 100
        
        # Mostrar tabela com os melhores segmentos
        st.dataframe(
            top_segments.sort_values(metric, ascending=False).head(10),
            column_config={
                "age": "Idade",
                "gender": "Gênero",
                "impressions": st.column_config.NumberColumn(format="%d"),
                "clicks": st.column_config.NumberColumn(format="%d"),
                "conversions": st.column_config.NumberColumn(format="%d"),
                "spend": st.column_config.NumberColumn(format="R$ %.2f"),
                "ctr": st.column_config.NumberColumn(format="%.2f%%"),
                "cpa": st.column_config.NumberColumn(format="R$ %.2f"),
                "conversion_rate": st.column_config.NumberColumn(format="%.2f%%")
            },
            hide_index=True
        )
    
    elif segment_type == 'geographic':
        st.markdown("#### 🌎 Distribuição Geográfica")
        
        # Mapa de calor por país/região
        geo_data = df.groupby(['country', 'region']).agg({
            metric: 'sum'
        }).reset_index()
        
        fig = px.choropleth(
            geo_data,
            locations='country',
            locationmode='country names',
            color=metric,
            hover_name='region',
            title=f"Distribuição de {metric.upper()} por Localização"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif segment_type == 'device':
        st.markdown("#### 📱 Distribuição por Dispositivo")
        
        device_data = df.groupby('device').agg({
            metric: 'sum'
        }).reset_index()
        
        fig = px.pie(
            device_data,
            names='device',
            values=metric,
            title=f"{metric.upper()} por Tipo de Dispositivo"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif segment_type == 'placement':
        st.markdown("#### 📍 Distribuição por Placement")
        
        placement_data = df.groupby('placement').agg({
            metric: 'sum'
        }).reset_index()
        
        fig = px.bar(
            placement_data.sort_values(metric, ascending=False),
            x='placement',
            y=metric,
            title=f"{metric.upper()} por Placement"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Análise de ROI por segmento
    st.markdown("### 📈 ROI por Segmento")
    
    if 'conversions' in df.columns and 'spend' in df.columns:
        roi_df = df.groupby(
            'age' if segment_type == 'demographic' else 
            'country' if segment_type == 'geographic' else
            'device' if segment_type == 'device' else
            'placement'
        ).agg({
            'spend': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        roi_df['cpa'] = roi_df['spend'] / roi_df['conversions']
        roi_df['roi'] = (roi_df['conversions'] * 100) / roi_df['spend']  # Simples - ajustar conforme valor de conversão
        
        fig = px.bar(
            roi_df.sort_values('roi', ascending=False),
            x=roi_df.columns[0],
            y='roi',
            title='ROI por Segmento (Quanto maior, melhor)',
            color='cpa',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)

def show_demographic_analysis(demographics):
    """Mostra análise detalhada por idade e gênero"""
    if not demographics:
        st.warning("Dados demográficos não disponíveis para este anúncio.")
        return
    
    st.markdown("## 👥 Análise Demográfica Detalhada")
    
    # Converter para DataFrame
    df = pd.DataFrame(demographics)
    
    # Verificar e limpar dados
    df = df[df['age'].notna()]
    df = df[df['age'] != 'N/A']
    
    # Calcular métricas derivadas
    df['ctr'] = (df['clicks'] / df['impressions'].replace(0, 1)) * 100
    df['conversion_rate'] = (df['conversions'] / df['clicks'].replace(0, 1)) * 100
    df['cost_per_conversion'] = df['spend'] / df['conversions'].replace(0, 1)
    
    # Função para ordenação correta das faixas etárias
    def age_sort_key(age_str):
        try:
            if age_str == '65+':
                return (65, 100)
            elif '-' in age_str:
                start, end = map(int, age_str.split('-'))
                return (start, end)
            else:
                age = int(age_str)
                return (age, age)
        except:
            return (999, 999)
    
    # Preparar análise por idade e gênero
    age_gender_analysis = df.groupby(['age', 'gender']).agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'conversions': 'sum',
        'spend': 'sum',
        'ctr': 'mean',
        'conversion_rate': 'mean',
        'cost_per_conversion': 'mean'
    }).reset_index()
    
    # Adicionar chave de ordenação e ordenar
    age_gender_analysis['sort_key'] = age_gender_analysis['age'].apply(age_sort_key)
    age_gender_analysis = age_gender_analysis.sort_values('sort_key')
    
    # Definir best_segment e worst_segment
    if not age_gender_analysis.empty:
        best_segment = age_gender_analysis.loc[age_gender_analysis['conversion_rate'].idxmax()]
        worst_segment = age_gender_analysis.loc[age_gender_analysis['conversion_rate'].idxmin()]
    else:
        st.warning("Não há dados suficientes para análise segmentada.")
        return
    
    # ... (restante do código de visualização permanece igual)

    # Recomendações baseadas nos dados
    st.markdown("### 💡 Recomendações de Segmentação")
    
    if best_segment['conversion_rate'] > 2 * worst_segment['conversion_rate']:
        st.success(f"""
        **Segmento de Alto Desempenho:**  
        {best_segment['gender'].capitalize()}s de {best_segment['age']} anos  
        - CTR: {best_segment['ctr']:.2f}%  
        - Taxa de Conversão: {best_segment['conversion_rate']:.2f}%  
        - Custo por Conversão: R${best_segment['cost_per_conversion']:.2f}
        
        **Ações Recomendadas:**
        - Aumentar investimento neste segmento
        - Criar campanhas específicas para este público
        - Desenvolver criativos similares para públicos adjacentes
        """)
    
    st.warning(f"""
    **Segmento de Baixo Desempenho:**  
    {worst_segment['gender'].capitalize()}s de {worst_segment['age']} anos  
    - CTR: {worst_segment['ctr']:.2f}%  
    - Taxa de Conversão: {worst_segment['conversion_rate']:.2f}%  
    - Custo por Conversão: R${worst_segment['cost_per_conversion']:.2f}
    
    **Ações Recomendadas:**
    - Revisar segmentação para este grupo
    - Testar mensagens diferentes
    - Considerar reduzir investimento ou excluir este segmento
    """)
    
    st.warning(f"""
    **Segmento de Baixo Desempenho:**  
    {worst_segment['gender'].capitalize()}s de {worst_segment['age']} anos  
    - CTR: {worst_segment['ctr']:.2f}%  
    - Taxa de Conversão: {worst_segment['conversion_rate']:.2f}%  
    - Custo por Conversão: R${worst_segment['cost_per_conversion']:.2f}
    
    **Ações Recomendadas:**
    - Revisar segmentação para este grupo
    - Testar mensagens diferentes
    - Considerar reduzir investimento ou excluir este segmento
    """)

def get_ad_insights_over_time(ad_id, date_range='last_30d'):
    """Obtém métricas diárias com tratamento seguro para campos ausentes"""
    try:
        # Campos base que geralmente estão disponíveis
        base_fields = [
            'date_start', 'impressions', 'reach', 'spend',
            'clicks', 'ctr', 'frequency', 'cpm'
        ]
        
        # Campos adicionais que podem não estar disponíveis
        optional_fields = [
            'conversions', 'cost_per_conversion',
            'unique_clicks', 'actions'
        ]
        
        # Primeira tentativa com todos os campos
        fields = base_fields + optional_fields
        
        if date_range == 'last_30d':
            since = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            until = datetime.now().strftime('%Y-%m-%d')
        elif date_range == 'last_7d':
            since = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            until = datetime.now().strftime('%Y-%m-%d')
        else:
            since, until = date_range.split('_to_')

        params = {
            'time_range': {'since': since, 'until': until},
            'level': 'ad',
            'time_increment': 1
        }

        ad = Ad(ad_id)
        insights = ad.get_insights(fields=fields, params=params)
        
        if not insights:
            return None

        # Processamento seguro dos dados
        data = []
        for insight in insights:
            row = {}
            for field in fields:
                # Tratamento especial para actions/conversions
                if field == 'actions':
                    actions = insight.get(field, [])
                    conversions = sum(float(a['value']) for a in actions 
                                  if a['action_type'] == 'conversion' and 'value' in a)
                    row['conversions'] = conversions
                else:
                    row[field] = insight.get(field, 0)
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Garantir tipos corretos
        df['date_start'] = pd.to_datetime(df['date_start'], errors='coerce')
        df = df.dropna(subset=['date_start']).sort_values('date_start')
        
        # Converter métricas numéricas
        for col in base_fields[1:] + optional_fields:
            if col in df.columns:
                df[col] = df[col].apply(safe_float)
        
        # Calcular métricas derivadas
        df['ctr'] = df['ctr'] * 100  # Converter para porcentagem
        df['cpc'] = np.where(df['clicks'] > 0, df['spend']/df['clicks'], 0)
        
        if 'conversions' in df.columns:
            df['conversion_rate'] = np.where(df['clicks'] > 0,
                                           (df['conversions']/df['clicks'])*100,
                                           0)
            df['cost_per_conversion'] = np.where(df['conversions'] > 0,
                                               df['spend']/df['conversions'],
                                               0)
        
        return df

    except Exception as e:
        st.error(f"Erro ao processar dados temporais: {str(e)}")
        return None

# ==============================================
# VISUALIZAÇÕES MELHORADAS
# ==============================================

def create_performance_gauge(value, min_val, max_val, title, color_scale=None):
    """Cria um medidor visual estilo gauge com escala de cores personalizável"""
    if color_scale is None:
        color_scale = {
            'axis': {'range': [min_val, max_val]},
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': (min_val + max_val) * 0.7
            },
            'steps': [
                {'range': [min_val, min_val*0.6], 'color': "red"},
                {'range': [min_val*0.6, min_val*0.8], 'color': "orange"},
                {'range': [min_val*0.8, max_val], 'color': "green"}]
        }
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number={'suffix': '%', 'font': {'size': 24}},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18}},
        gauge=color_scale
    ))
    fig.update_layout(margin=dict(t=50, b=10))
    return fig

def create_trend_chart(df, x_col, y_cols, title, mode='lines'):
    """Cria gráfico de tendência temporal com múltiplas métricas"""
    fig = px.line(df, x=x_col, y=y_cols, title=title,
                 line_shape='spline', render_mode='svg')
    
    fig.update_layout(
        hovermode='x unified',
        legend_title_text='Métrica',
        xaxis_title='Data',
        yaxis_title='Valor',
        plot_bgcolor='rgba(240,240,240,0.9)'
    )
    
    # Adiciona anotações para pontos máximos e mínimos
    for col in y_cols:
        max_val = df[col].max()
        min_val = df[col].min()
        
        max_date = df.loc[df[col] == max_val, x_col].values[0]
        min_date = df.loc[df[col] == min_val, x_col].values[0]
        
        fig.add_annotation(x=max_date, y=max_val,
                          text=f"Max: {max_val:.2f}",
                          showarrow=True,
                          arrowhead=1)
        
        fig.add_annotation(x=min_date, y=min_val,
                          text=f"Min: {min_val:.2f}",
                          showarrow=True,
                          arrowhead=1)
    
    return fig

def show_video_analysis(demographics):
    """Mostra análise de performance de vídeos por demografia"""
    video_data = [d for d in demographics if 'video_views' in d and d['video_views'] > 0]
    
    if not video_data:
        return
    
    st.markdown("## 🎥 Análise de Performance de Vídeo")
    
    df = pd.DataFrame(video_data)
    
    # Métricas de vídeo por idade
    st.markdown("### 📉 Retenção por Faixa Etária")
    
    video_metrics = df.groupby('age').agg({
        'video_views': 'sum',
        'video_completion_25': 'sum',
        'video_completion_50': 'sum',
        'video_completion_75': 'sum',
        'video_completion_95': 'sum',
        'avg_watch_time': 'mean'
    }).reset_index()
    
    # Calcular taxas de conclusão
    for p in [25, 50, 75, 95]:
        video_metrics[f'completion_{p}_rate'] = (video_metrics[f'video_completion_{p}'] / video_metrics['video_views']) * 100
    
    # Gráfico de retenção
    fig_retention = px.line(
        video_metrics,
        x='age',
        y=['completion_25_rate', 'completion_50_rate', 'completion_75_rate', 'completion_95_rate'],
        title='Taxas de Conclusão do Vídeo por Idade',
        labels={'value': 'Percentual de Conclusão', 'variable': 'Ponto do Vídeo'},
        markers=True
    )
    st.plotly_chart(fig_retention, use_container_width=True)
    
    # Análise por gênero
    st.markdown("### ♀️♂️ Engajamento por Gênero")
    
    gender_video = df.groupby('gender').agg({
        'video_views': 'sum',
        'avg_watch_time': 'mean',
        'video_completion_95': 'sum'
    }).reset_index()
    
    gender_video['completion_rate'] = (gender_video['video_completion_95'] / gender_video['video_views']) * 100
    
    col1, col2 = st.columns(2)
    with col1:
        fig_gender_views = px.pie(
            gender_video,
            names='gender',
            values='video_views',
            title='Visualizações por Gênero'
        )
        st.plotly_chart(fig_gender_views, use_container_width=True)
    
    with col2:
        fig_gender_time = px.bar(
            gender_video,
            x='gender',
            y='avg_watch_time',
            title='Tempo Médio de Visualização',
            color='gender',
            color_discrete_map={'male': 'blue', 'female': 'pink'}
        )
        st.plotly_chart(fig_gender_time, use_container_width=True)
    
    # Recomendações baseadas nos dados
    st.markdown("### 💡 Recomendações para Vídeos")
    
    best_age = video_metrics.loc[video_metrics['completion_95_rate'].idxmax()]['age']
    worst_age = video_metrics.loc[video_metrics['completion_95_rate'].idxmin()]['age']
    
    st.info(f"""
    **Melhor performance:** {best_age} anos ({video_metrics['completion_95_rate'].max():.1f}% conclusão)  
    **Pior performance:** {worst_age} anos ({video_metrics['completion_95_rate'].min():.1f}% conclusão)
    
    **Ações sugeridas:**
    - Criar versões mais curtas para o público de {worst_age} anos
    - Testar hooks diferentes nos primeiros 3 segundos
    - Analisar o momento de drop-off para cada faixa etária
    """)

def create_benchmark_comparison(current_values, benchmark_values, labels):
    """Cria gráfico de comparação com benchmarks do setor"""
    fig = go.Figure()
    
    for i, (current, benchmark, label) in enumerate(zip(current_values, benchmark_values, labels)):
        fig.add_trace(go.Bar(
            x=[f"{label}"],
            y=[current],
            name='Seu Anúncio',
            marker_color='#1f77b4',
            showlegend=(i == 0)
        ))
        
        fig.add_trace(go.Bar(
            x=[f"{label}"],
            y=[benchmark],
            name='Benchmark Setor',
            marker_color='#ff7f0e',
            showlegend=(i == 0)
        ))
    
    fig.update_layout(
        barmode='group',
        title='Comparação com Benchmarks do Setor',
        yaxis_title='Valor',
        plot_bgcolor='rgba(240,240,240,0.9)'
    )
    
    return fig

def generate_performance_recommendations(insights, temporal_data):
    """Gera recomendações estratégicas baseadas em métricas"""
    recommendations = []
    
    # Análise de CTR
    ctr = safe_float(insights.get('ctr', 0)) * 100
    if ctr < 0.8:
        recommendations.append({
            'type': 'error',
            'title': 'CTR Baixo',
            'message': f"CTR de {ctr:.2f}% está abaixo do benchmark recomendado (1-2%)",
            'actions': [
                "Teste diferentes imagens/thumbnails no criativo",
                "Reduza o texto principal (ideal <125 caracteres)",
                "Posicione o CTA de forma mais destacada",
                "Teste diferentes cópias de texto"
            ]
        })
    elif ctr > 2.5:
        recommendations.append({
            'type': 'success',
            'title': 'CTR Alto',
            'message': f"Excelente CTR de {ctr:.2f}%!",
            'actions': [
                "Aumente o orçamento para escalar este desempenho",
                "Replique a estratégia para públicos similares",
                "Documente as características deste anúncio"
            ]
        })
    
    # Análise de Custo por Conversão
    cost_per_conv = safe_float(insights.get('cost_per_conversion', 0))
    if cost_per_conv > 50:
        recommendations.append({
            'type': 'error',
            'title': 'Custo Alto por Conversão',
            'message': f"R${cost_per_conv:.2f} por conversão (acima da média)",
            'actions': [
                "Otimize a landing page (taxa de conversão pode estar baixa)",
                "Ajuste a segmentação para públicos mais qualificados",
                "Teste diferentes objetivos de campanha",
                "Verifique a qualidade do tráfego"
            ]
        })
    
    # Análise de Frequência (se houver dados temporais)
    if temporal_data is not None:
        freq = temporal_data['frequency'].mean()
        if freq > 3.5:
            recommendations.append({
                'type': 'warning',
                'title': 'Frequência Elevada',
                'message': f"Média de {freq:.1f} impressões por usuário (risco de fadiga)",
                'actions': [
                    "Reduza o orçamento ou pause temporariamente",
                    "Atualize o criativo para evitar saturação",
                    "Expanda o público-alvo"
                ]
            })
    
    return recommendations

# ==============================================
# INTERFACES DE USUÁRIO PARA ANÁLISE REAL
# ==============================================

def show_real_analysis():
    st.markdown("## 🔍 Análise de Anúncios Reais - Meta Ads")
    
    # Inicializa a API com as credenciais do usuário
    ad_account = init_facebook_api()
    if not ad_account:
        return  # Sai se as credenciais não foram fornecidas
    
    # Restante do código permanece igual...
    date_range = st.radio("Período de análise:", 
                         ["Últimos 7 dias", "Últimos 30 dias", "Personalizado"],
                         index=1, horizontal=True)
    
    custom_range = None
    if date_range == "Personalizado":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data inicial", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("Data final", datetime.now())
        custom_range = f"{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}"
    
    date_range_param = {
        "Últimos 7 dias": "last_7d",
        "Últimos 30 dias": "last_30d",
        "Personalizado": custom_range
    }[date_range]
    
    with st.spinner("Carregando campanhas..."):
        campaigns = get_campaigns(ad_account)
        
        if campaigns and st.toggle('Mostrar dados brutos (debug)'):
            st.write("Dados brutos das campanhas:", campaigns)

    if not campaigns:
        st.warning("Nenhuma campanha encontrada nesta conta.")
        return
    
    selected_campaign = st.selectbox(
        "Selecione uma campanha:",
        options=campaigns,
        format_func=lambda x: f"{x.get('name', 'Sem Nome')} (ID: {x.get('id', 'N/A')})",
        key='campaign_select'
    )
    
    with st.spinner("Carregando conjuntos de anúncios..."):
        adsets = get_adsets(selected_campaign['id'])
    
    if not adsets:
        st.warning("Nenhum conjunto de anúncios encontrado nesta campanha.")
        return
    
    selected_adset = st.selectbox(
        "Selecione um conjunto de anúncios:",
        options=adsets,
        format_func=lambda x: f"{x.get('name', 'Sem Nome')} (ID: {x.get('id', 'N/A')})"
    )
    
    with st.spinner("Carregando anúncios..."):
        ads = get_ads(selected_adset['id'])
    
    if not ads:
        st.warning("Nenhum anúncio encontrado neste conjunto.")
        return
    
    selected_ad = st.selectbox(
        "Selecione um anúncio para análise:",
        options=ads,
        format_func=lambda x: f"{x.get('name', 'Sem Nome')} (ID: {x.get('id', 'N/A')})"
    )
    
    if st.button("🔍 Analisar Anúncio", type="primary"):
        with st.spinner("Coletando dados do anúncio..."):
            ad_details = {
                'id': selected_ad['id'],
                'name': selected_ad.get('name', 'N/A'),
                'status': selected_ad.get('status', 'N/A'),
                'created_time': selected_ad.get('created_time', 'N/A'),
                'bid_amount': selected_ad.get('bid_amount', 'N/A'),
                'campaign_id': selected_campaign['id'],
                'campaign_name': selected_campaign.get('name', 'N/A'),
                'campaign_objective': selected_campaign.get('objective', 'N/A'),
                'adset_id': selected_adset['id'],
                'adset_name': selected_adset.get('name', 'N/A'),
                'adset_budget': selected_adset.get('daily_budget', 'N/A'),
                'adset_optimization': selected_adset.get('optimization_goal', 'N/A')
            }
            
            ad_insights = get_ad_insights(selected_ad['id'], date_range_param)
            ad_demographics = get_ad_demographics(selected_ad['id'], date_range_param)
            temporal_data = get_ad_insights_over_time(selected_ad['id'], date_range_param)
            
            if ad_insights:
                show_ad_results(ad_details, ad_insights, ad_demographics, date_range_param, temporal_data)
            else:
                st.error("Não foi possível obter dados de desempenho para este anúncio.")

def show_ad_results(details, insights, demographics, date_range, temporal_data=None):
    st.success(f"✅ Dados obtidos com sucesso para o anúncio {details['id']}")
    
    # Seção de detalhes do anúncio
    st.markdown("### 📝 Detalhes do Anúncio")
    cols = st.columns(4)
    cols[0].metric("Nome do Anúncio", details.get('name', 'N/A'))
    cols[1].metric("Campanha", details.get('campaign_name', 'N/A'))
    cols[2].metric("Conjunto", details.get('adset_name', 'N/A'))
    cols[3].metric("Status", details.get('status', 'N/A'))
    
    cols = st.columns(4)
    cols[0].metric("Objetivo", details.get('campaign_objective', 'N/A'))
    cols[1].metric("Otimização", details.get('adset_optimization', 'N/A'))
    cols[2].metric("Lance", f"R$ {safe_float(details.get('bid_amount', 0)):.2f}")
    cols[3].metric("Orçamento Diário", f"R$ {safe_float(details.get('adset_budget', 0)):.2f}")
    
    # Seção de métricas de desempenho
    st.markdown("### 📊 Métricas de Desempenho")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Performance","📈 Tendências","👥 Público","🧠 Recomendações IA","🔍 Análise Demográfica"])
    
    with tab1:
        # Métricas principais em colunas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ctr = safe_float(insights.get('ctr', 0)) * 100
            st.plotly_chart(create_performance_gauge(
                ctr, 0, 10, 
                f"CTR: {ctr:.2f}%"), 
                use_container_width=True)
        
        with col2:
            conversions = safe_float(insights.get('conversions', 0))
            clicks = safe_float(insights.get('clicks', 0))
            conversion_rate = (conversions / clicks) * 100 if clicks > 0 else 0
            st.plotly_chart(create_performance_gauge(
                conversion_rate, 0, 20, 
                f"Taxa de Conversão: {conversion_rate:.2f}%"), 
                use_container_width=True)
        
        with col3:
            spend = safe_float(insights.get('spend', 0))
            conversions = safe_float(insights.get('conversions', 0))
            cost_per_conversion = spend / conversions if conversions > 0 else 0
            st.plotly_chart(create_performance_gauge(
                cost_per_conversion, 0, 100, 
                f"Custo por Conversão: R${cost_per_conversion:.2f}"), 
                use_container_width=True)
            
        # Outras métricas em colunas
        cols = st.columns(4)
        metrics = [
            ("Impressões", safe_int(insights.get('impressions', 0)), "{:,}"),
            ("Alcance", safe_int(insights.get('reach', 0)), "{:,}"),
            ("Frequência", safe_float(insights.get('frequency', 0)), "{:.2f}x"),
            ("Investimento", safe_float(insights.get('spend', 0)), "R$ {:,.2f}"),
            ("CPM", safe_float(insights.get('cpm', 0)), "R$ {:.2f}"),
            ("CPC", safe_float(insights.get('cost_per_unique_click', insights.get('cpp', 0))), "R$ {:.2f}"),
            ("Cliques", safe_int(insights.get('clicks', 0)), "{:,}"),
            ("Cliques Únicos", safe_int(insights.get('unique_outbound_clicks', 0)), "{:,}")
        ]
        
        for i, (label, value, fmt) in enumerate(metrics):
            cols[i % 4].metric(label, fmt.format(value))
    
    with tab2:
        if temporal_data is not None:
            st.subheader("📈 Análise Temporal Detalhada")

            available_metrics = ['impressions', 'reach', 'spend', 'clicks',
                                 'ctr', 'conversions', 'cost_per_conversion',
                                 'frequency', 'cpm', 'cpc', 'conversion_rate']

            selected_metrics = st.multiselect(
                "Selecione métricas para visualizar:",
                options=available_metrics,
                default=['impressions', 'spend', 'conversions'],
                key='temp_metrics_unique_key'
            )

            if selected_metrics:
                # Gráfico de linhas principal
                fig = px.line(
                    temporal_data,
                    x='date_start',
                    y=selected_metrics,
                    title='Desempenho ao Longo do Tempo',
                    markers=True,
                    line_shape='spline'
                )
                fig.update_layout(
                    hovermode='x unified',
                    yaxis_title='Valor',
                    xaxis_title='Data'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Análise de correlação
                st.subheader("🔍 Correlação Entre Métricas")
                corr_matrix = temporal_data[selected_metrics].corr()
                fig_corr = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect='auto',
                    color_continuous_scale='RdBu',
                    labels=dict(color='Correlação')
                )
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Melhores dias por métrica
                st.subheader("🏆 Melhores Dias")
                best_days = []
                for metric in selected_metrics:
                    best_day = temporal_data.loc[temporal_data[metric].idxmax()]
                    if pd.api.types.is_datetime64_any_dtype(best_day['date_start']):
                        date_str = best_day['date_start'].strftime('%Y-%m-%d')
                    else:
                        date_str = pd.to_datetime(best_day['date_start']).strftime('%Y-%m-%d')
                    
                    best_days.append({
                        'Métrica': metric,
                        'Data': best_day['date_start'].strftime('%Y-%m-%d'),
                        'Valor': best_day[metric],
                        'Investimento': best_day['spend']
                    })
                
                st.dataframe(pd.DataFrame(best_days), hide_index=True)
        else:
            st.warning("Dados temporais não disponíveis para este anúncio.")

    with tab3:
        # Mostra ações específicas e seus valores
        st.markdown("#### 🎯 Ações Específicas Registradas")
        
        # Filtra todas as chaves que começam com 'action_' ou 'action_value_'
        actions = {k: v for k, v in insights.items() if k.startswith('action_') or k.startswith('action_value_')}
        
        if actions:
            # Agrupa ações e valores
            action_types = set([k.split('_', 1)[1] for k in actions.keys()])
            
            for action_type in action_types:
                action_count = safe_int(actions.get(f'action_{action_type}', 0))
                action_value = safe_float(actions.get(f'action_value_{action_type}', 0))
                
                cols = st.columns(2)
                cols[0].metric(f"🔹 {action_type.replace('_', ' ').title()}", action_count)
                cols[1].metric(f"💰 Valor Total", f"R$ {action_value:.2f}")
        else:
            st.info("Nenhuma ação específica registrada para este anúncio no período selecionado")
        with tab4:  # Nova aba de recomendações com IA
            st.markdown("## 🧠 Recomendações de Otimização Inteligente")
        
        with st.spinner("Analisando métricas e gerando recomendações personalizadas..."):
            recommendations = generate_ai_optimization_recommendations(
                details, insights, temporal_data, demographics
            )
        
        if not recommendations:
            st.success("✅ Seu anúncio está performando acima dos benchmarks em todas as métricas-chave!")
        else:
            for rec in recommendations:
                with st.expander(f"🔴 {rec['title']}" if rec['severity'] == 'high' else 
                              f"🟠 {rec['title']}" if rec['severity'] == 'medium' else 
                              f"🔵 {rec['title']}", expanded=True):
                    
                    st.markdown(f"**📊 Diagnóstico:** {rec['diagnosis']}")
                    
                    st.markdown("**🛠 Ações Recomendadas:**")
                    for action in rec['actions']:
                        st.markdown(f"- {action}")
                    
                    cols = st.columns(2)
                    with cols[0]:
                        st.metric("📈 Impacto Esperado", rec['expected_impact'])
                    with cols[1]:
                        st.metric("⏱ Prazo Estimado", rec['timeframe'])
                    
                    if rec['severity'] == 'high':
                        st.error("Prioridade máxima - resolver imediatamente")
                    elif rec['severity'] == 'medium':
                        st.warning("Prioridade média - resolver nesta semana")
                    else:
                        st.info("Prioridade baixa - considerar no próximo ciclo")
            
            # Plano de ação executivo
            st.markdown("### 🚀 Plano de Ação Prioritário")
            action_plan = pd.DataFrame([
                {
                    'Prioridade': 'Alta' if r['severity'] == 'high' else 'Média' if r['severity'] == 'medium' else 'Baixa',
                    'Ação': r['actions'][0],
                    'Responsável': 'Equipe de Criativos' if 'criativo' in r['title'].lower() else 'Gestor de Tráfego',
                    'Prazo': r['timeframe']
                }
                for r in recommendations
            ])
            st.dataframe(action_plan.sort_values('Prioridade'), hide_index=True, use_container_width=True)

    with tab5:
    # Verifica se demographics existe e é uma lista
        if demographics and isinstance(demographics, list):
        # Filtra apenas itens com age e gender
            valid_demographics = [d for d in demographics if 'age' in d and 'gender' in d]
        
            if valid_demographics:
                show_demographic_analysis(valid_demographics)
            else:
                st.warning("Dados demográficos não contêm informações de idade e gênero.")
        else:
            st.warning("Dados demográficos não disponíveis para este anúncio.")

    # Seção de análise demográfica
    if demographics:
        st.markdown("### 👥 Demografia do Público")
        
        # Separa dados por age/gender e country
        age_gender_data = [d for d in demographics if 'age' in d and 'gender' in d]
        country_data = [d for d in demographics if 'country' in d]
        
        if age_gender_data:
            df_age_gender = pd.DataFrame([
                {
                    'age': d.get('age', 'N/A'),
                    'gender': d.get('gender', 'N/A'),
                    'impressions': safe_int(d.get('impressions', 0)),
                    'clicks': safe_int(d.get('clicks', 0)),
                    'spend': safe_float(d.get('spend', 0)),
                    'conversions': safe_int(d.get('conversions', 0))
                }
                for d in age_gender_data
            ])
            
            # Calcula métricas derivadas
            df_age_gender['CTR'] = df_age_gender['clicks'] / df_age_gender['impressions'].replace(0, 1) * 100
            df_age_gender['CPM'] = (df_age_gender['spend'] / df_age_gender['impressions'].replace(0, 1)) * 1000
            
            st.markdown("#### Distribuição por Idade e Gênero")
            pivot_age_gender = df_age_gender.groupby(['age', 'gender'])['impressions'].sum().unstack()
            st.plotly_chart(
                px.bar(pivot_age_gender, barmode='group', 
                      labels={'value': 'Impressões', 'age': 'Faixa Etária'},
                      title='Impressões por Faixa Etária e Gênero'),
                use_container_width=True
            )
        
        if country_data:
            df_country = pd.DataFrame([
                {
                    'country': d.get('country', 'N/A'),
                    'impressions': safe_int(d.get('impressions', 0)),
                    'clicks': safe_int(d.get('clicks', 0)),
                    'spend': safe_float(d.get('spend', 0)),
                    'conversions': safe_int(d.get('conversions', 0))
                }
                for d in country_data
            ])
            
            df_country['CPM'] = (df_country['spend'] / df_country['impressions'].replace(0, 1)) * 1000
            
            st.markdown("#### Distribuição por País")
            country_dist = df_country.groupby('country')['impressions'].sum().nlargest(10)
            st.plotly_chart(
                px.pie(country_dist, values='impressions', names=country_dist.index,
                      title='Top 10 Países por Impressões'),
                use_container_width=True
            )
    
    # Chamada para a nova análise estratégica
    generate_strategic_analysis(details, insights, demographics, temporal_data)
    
    # Seção de recomendações (mantida para compatibilidade)
    st.markdown("### 💡 Recomendações de Otimização")
    
    recommendations = generate_performance_recommendations(insights, temporal_data)
    
    if not recommendations:
        st.success("✅ Seu anúncio está performando dentro ou acima dos benchmarks!")
        st.write("Ações recomendadas para manter o bom desempenho:")
        st.write("- Continue monitorando as métricas regularmente")
        st.write("- Teste pequenas variações para otimização contínua")
        st.write("- Considere aumentar o orçamento para escalar")
    else:
        for rec in recommendations:
            if rec['type'] == 'error':
                st.error(f"#### {rec['title']}: {rec['message']}")
            elif rec['type'] == 'warning':
                st.warning(f"#### {rec['title']}: {rec['message']}")
            else:
                st.success(f"#### {rec['title']}: {rec['message']}")
            
            st.write("**Ações recomendadas:**")
            for action in rec['actions']:
                st.write(f"- {action}")
    
    # Seção de próximos passos
    st.markdown("### 🚀 Próximos Passos")
    st.write("1. **Implemente as mudanças sugeridas** de forma gradual")
    st.write("2. **Monitore os resultados** diariamente por 3-5 dias")
    st.write("3. **Documente os aprendizados** para cada variação testada")
    st.write("4. **Escalone o que funciona** e pause o que não performa")
    
    if temporal_data is not None:
        st.download_button(
            label="📥 Baixar Dados Completos",
            data=temporal_data.to_csv(index=False).encode('utf-8'),
            file_name=f"dados_anuncio_{details['id']}.csv",
            mime='text/csv'
        )

# ==============================================
# ANÁLISE ESTRATÉGICA AVANÇADA
# ==============================================

def generate_strategic_analysis(ad_details, insights, demographics, temporal_data):
    """Gera uma análise estratégica completa com recomendações baseadas em dados"""
    
    # Cálculos preliminares com proteção contra divisão por zero
    ctr = safe_float(insights.get('ctr', 0)) * 100 if safe_float(insights.get('impressions', 0)) > 0 else 0
    clicks = safe_float(insights.get('clicks', 0))
    conversions = safe_float(insights.get('conversions', 0))
    spend = safe_float(insights.get('spend', 0))
    impressions = safe_float(insights.get('impressions', 0))
    
    conversion_rate = (conversions / clicks) * 100 if clicks > 0 else 0
    cost_per_conversion = spend / conversions if conversions > 0 else 0
    cpm = (spend / impressions) * 1000 if impressions > 0 else 0
    cpc = spend / clicks if clicks > 0 else 0
    
    # Benchmarks do setor (podem ser ajustados conforme o objetivo da campanha)
    benchmarks = {
        'ctr': 2.0,
        'conversion_rate': 3.0,
        'cost_per_conversion': 50.0,
        'cpm': 10.0,
        'cpc': 1.5
    }
    
    # Análise de frequência (se houver dados temporais)
    freq_mean = temporal_data['frequency'].mean() if temporal_data is not None else 0
    
    with st.expander("🔍 Análise Estratégica Completa", expanded=True):
        
        # Seção 1: Diagnóstico de Performance
        st.subheader("📊 Diagnóstico de Performance")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("CTR", f"{ctr:.2f}%", 
                     delta=f"{'↑' if ctr > benchmarks['ctr'] else '↓'} vs benchmark {benchmarks['ctr']}%",
                     delta_color="inverse")
        
        with col2:
            st.metric("Taxa de Conversão", f"{conversion_rate:.2f}%",
                     delta=f"{'↑' if conversion_rate > benchmarks['conversion_rate'] else '↓'} vs benchmark {benchmarks['conversion_rate']}%",
                     delta_color="inverse")
        
        with col3:
            st.metric("Custo por Conversão", f"R${cost_per_conversion:.2f}",
                     delta=f"{'↓' if cost_per_conversion < benchmarks['cost_per_conversion'] else '↑'} vs benchmark R${benchmarks['cost_per_conversion']}",
                     delta_color="inverse")
        
        # Seção 2: Pontos Fortes Identificados
        st.subheader("✅ Pontos Fortes Identificados")
        
        strengths = []
        
        # Identificar pontos fortes com base nos dados
        if ctr > benchmarks['ctr'] * 1.2:
            strengths.append(f"CTR excelente ({ctr:.2f}%) - {ctr/benchmarks['ctr']:.1f}x acima da média")
        
        if conversion_rate > benchmarks['conversion_rate'] * 1.2:
            strengths.append(f"Taxa de conversão alta ({conversion_rate:.2f}%) - Eficiência no funnel")
        
        if cost_per_conversion < benchmarks['cost_per_conversion'] * 0.8:
            strengths.append(f"Custo por conversão baixo (R${cost_per_conversion:.2f}) - Eficiência de gastos")
        
        if demographics:
            # Verificar se há segmentos com performance excepcional
            df_age_gender = pd.DataFrame([
                {
                'age': d.get('age', 'N/A'),
                'gender': d.get('gender', 'N/A'),
                'ctr': (safe_int(d.get('clicks', 0)) / safe_int(d.get('impressions', 1)) * 100) if safe_int(d.get('impressions', 0)) > 0 else 0,
                'conversion_rate': (safe_int(d.get('conversions', 0)) / safe_int(d.get('clicks', 1)) * 100) if safe_int(d.get('clicks', 0)) > 0 else 0,
                'cpa': safe_int(d.get('spend', 0)) / max(1, safe_int(d.get('conversions', 0)))
            }
            for d in demographics if 'age' in d and 'gender' in d
        ])
            
            if not df_age_gender.empty:
             top_segment = df_age_gender.loc[df_age_gender['ctr'].idxmax()]
            if top_segment['ctr'] > benchmarks['ctr'] * 1.5:
                strengths.append(f"Segmento de alto desempenho: {top_segment['gender']} {top_segment['age']} (CTR: {top_segment['ctr']:.2f}%)")

        if strengths:
            for strength in strengths:
                st.success(f"- {strength}")
        else:
            st.info("Nenhum ponto forte excepcional identificado. Foque em otimizações básicas.")
        
        # Seção 3: Oportunidades de Melhoria
        st.subheader("🔧 Oportunidades de Melhoria")
        
        improvements = []
        
        if ctr < benchmarks['ctr'] * 0.8:
            improvements.append(f"CTR baixo ({ctr:.2f}%) - Testar novos criativos e chamadas para ação")
        
        if conversion_rate < benchmarks['conversion_rate'] * 0.8:
            improvements.append(f"Taxa de conversão baixa ({conversion_rate:.2f}%) - Otimizar landing page e jornada do usuário")
        
        if cost_per_conversion > benchmarks['cost_per_conversion'] * 1.2:
            improvements.append(f"Custo por conversão alto (R${cost_per_conversion:.2f}) - Refinar público-alvo e segmentação")
        
        if freq_mean > 3.5:
            improvements.append(f"Frequência alta ({freq_mean:.1f}x) - Risco de saturação, considere atualizar criativos ou expandir público")
        
        if improvements:
            for improvement in improvements:
                st.error(f"- {improvement}")
        else:
            st.success("Performance geral dentro ou acima dos benchmarks. Considere escalar campanhas bem-sucedidas.")
        
        # Seção 4: Recomendações Específicas por Tipo de Anúncio
        st.subheader("🎯 Recomendações Específicas")
        
        # Baseado no tipo de campanha (do adset ou campaign)
        campaign_objective = ad_details.get('campaign_objective', '').lower()
        
        if 'conversion' in campaign_objective:
            st.write("""
            **Para campanhas de conversão:**
            - Teste diferentes CTAs na landing page
            - Implemente eventos de conversão secundários
            - Otimize para públicos similares a convertidos
            """)
        elif 'awareness' in campaign_objective:
            st.write("""
            **Para campanhas de awareness:**
            - Aumente o alcance com formatos de vídeo
            - Utilize o recurso de expansão de público
            - Monitore a frequência para evitar saturação
            """)
        else:
            st.write("""
            **Recomendações gerais:**
            - Teste pelo menos 3 variações de criativos
            - Experimente diferentes horários de veiculação
            - Ajuste bids conforme performance por segmento
            """)
        
        # Seção 5: Plano de Ação Priorizado
        st.subheader("📅 Plano de Ação Priorizado")
        
        action_plan = []
        
        # Prioridade 1: CTR baixo
        if ctr < benchmarks['ctr'] * 0.8:
            action_plan.append({
                "Prioridade": "Alta",
                "Ação": "Otimizar CTR",
                "Tarefas": [
                    "Criar 3 variações de imagens/thumbnails",
                    "Testar diferentes textos principais (max 125 chars)",
                    "Posicionar CTA mais destacado"
                ],
                "Prazo": "3 dias",
                "Métrica Esperada": f"Aumentar CTR para ≥ {benchmarks['ctr']}%"
            })
        
        # Prioridade 2: Conversão baixa
        if conversion_rate < benchmarks['conversion_rate'] * 0.8:
            action_plan.append({
                "Prioridade": "Alta",
                "Ação": "Melhorar Taxa de Conversão",
                "Tarefas": [
                    "Otimizar landing page (velocidade, design, CTA)",
                    "Implementar pop-ups inteligentes",
                    "Simplificar formulários de conversão"
                ],
                "Prazo": "5 dias",
                "Métrica Esperada": f"Aumentar conversão para ≥ {benchmarks['conversion_rate']}%"
            })
        
        # Prioridade 3: Frequência alta
        if freq_mean > 3.5:
            action_plan.append({
                "Prioridade": "Média",
                "Ação": "Reduzir Saturação",
                "Tarefas": [
                    "Atualizar criativos principais",
                    "Expandir público-alvo",
                    "Ajustar orçamento por horário"
                ],
                "Prazo": "2 dias",
                "Métrica Esperada": f"Reduzir frequência para ≤ 3x"
            })
        
        # Se não houver problemas críticos, sugerir otimizações padrão
        if not action_plan:
            action_plan.append({
                "Prioridade": "Otimização",
                "Ação": "Escalonar Performance",
                "Tarefas": [
                    "Aumentar orçamento em 20% para melhores performers",
                    "Criar públicos lookalike baseados em convertidos",
                    "Testar novos formatos criativos"
                ],
                "Prazo": "Contínuo",
                "Métrica Esperada": "Manter ROAS ≥ 2.0"
            })
        
        st.table(pd.DataFrame(action_plan))
        
        # Seção 6: Projeção de Resultados
        st.subheader("📈 Projeção de Resultados")
        
        if temporal_data is not None:
            # Calcular crescimento médio diário
            last_7_days = temporal_data.tail(7)
            growth_rates = {
                'impressions': last_7_days['impressions'].pct_change().mean() * 100,
                'ctr': last_7_days['ctr'].pct_change().mean() * 100,
                'conversions': last_7_days['conversions'].pct_change().mean() * 100
            }
            
            projections = {
                "Cenário": ["Conservador", "Otimista", "Pessimista"],
                "Impressões (7 dias)": [
                    f"{impressions * 0.9:,.0f}",
                    f"{impressions * 1.3:,.0f}",
                    f"{impressions * 0.7:,.0f}"
                ],
                "Conversões (7 dias)": [
                    f"{conversions * 0.9:,.0f}",
                    f"{conversions * 1.5:,.0f}",
                    f"{conversions * 0.6:,.0f}"
                ],
                "Investimento": [
                    f"R${spend * 0.9:,.2f}",
                    f"R${spend * 1.5:,.2f}",
                    f"R${spend * 0.7:,.2f}"
                ],
                "ROI Esperado": [
                    f"{(conversions * 0.9 * 100) / max(1, spend * 0.9):.1f}%",
                    f"{(conversions * 1.5 * 100) / max(1, spend * 1.5):.1f}%",
                    f"{(conversions * 0.6 * 100) / max(1, spend * 0.7):.1f}%"
                ]
            }
            
            st.table(pd.DataFrame(projections))
            
            st.caption(f"*Baseado em crescimento médio atual: CTR {growth_rates['ctr']:.1f}% ao dia, Conversões {growth_rates['conversions']:.1f}% ao dia*")
        
        # Seção 7: Checklist de Implementação
        st.subheader("✅ Checklist de Implementação")
        
        checklist_items = [
            "Definir KPI principal e secundários",
            "Configurar eventos de conversão no Pixel",
            "Estabelecer orçamento diário mínimo para testes",
            "Criar pelo menos 3 variações de criativos",
            "Segmentar públicos por desempenho histórico",
            "Configurar relatórios automáticos de performance",
            "Estabelecer frequência de análise (recomendado diária)"
        ]
        
        for item in checklist_items:
            st.checkbox(item, key=f"check_{hashlib.md5(item.encode()).hexdigest()}")

# ==============================================
# FUNÇÃO PRINCIPAL SIMPLIFICADA
# ==============================================

def main():
    st.title("🚀 Meta Ads Analyzer Pro")
    st.markdown("""
    **Ferramenta avançada para análise de desempenho de anúncios no Meta (Facebook e Instagram)**
    """)
    
    # Mostra instruções de como obter as credenciais
    with st.expander("ℹ️ Como obter minhas credenciais?", expanded=False):
        st.markdown("""
        Para usar esta ferramenta, você precisará das seguintes credenciais da API do Meta:
        
        1. **App ID** e **App Secret**:  
           - Vá para [Facebook Developers](https://developers.facebook.com/)  
           - Selecione seu aplicativo ou crie um novo  
           - Encontre essas informações em "Configurações" > "Básico"
        
        2. **Access Token**:  
           - No mesmo painel, vá para "Ferramentas" > "Explorador de API"  
           - Selecione seu aplicativo  
           - Gere um token de acesso de longo prazo com permissões ads_management
        
        3. **Ad Account ID**:  
           - Vá para [Meta Ads Manager](https://adsmanager.facebook.com/)  
           - Selecione sua conta de anúncios  
           - O ID estará na URL (após /act_) ou em "Configurações da Conta"
        
        *Observação: Suas credenciais são usadas apenas localmente e não são armazenadas.*
        """)
    
    # Menu simplificado - apenas a opção de análise via API
    st.sidebar.info("Acesse dados completos dos seus anúncios via API")
    show_real_analysis()

if __name__ == "__main__":
    main()
