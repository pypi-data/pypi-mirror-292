import{c as We,p as Ft,d as Je,r as p,j as n,R as W,n as Pn,a as Me,C as Fe,b as Z,s as _t,e as Pt,f as ie,g as Te,h as ze,i as De,k as Le,l as Vt,m as Nt,o as ae,q as Rt,t as Ot,u as At,v as s,w as m,x as Pe,$ as _,L as Vn,y as Kt,z as zt,A as $t,B as Gt,D as dn,F as Ve,E as se,G as Bt,H as Qt,I as Nn,S as Ut,J as Ht,Q as un,K as Zt,M as jt,N as qt,P as $e,O as Rn,T as Wt,U as Jt,V as Xt,W as Yt,X as ea,Y as na,Z as ta,_ as aa,a0 as ra,a1 as Ne,a2 as N,a3 as On,a4 as ia,a5 as la,a6 as oa,a7 as sa,a8 as ca}from"./vendor-aSQri0vz.js";import{u as da,_ as q,a as xe,b as Q,c as O,T as A,F as An,d as $,I,e as w,f as B,A as ua,g as Kn,h as C,i as D,j as R,k as ma,l as pa,P as ga,R as H,m as Re,n as ha,o as fa,L as Xe,p as J,q as X,r as we,s as La,t as zn,E as $n,v as ya,w as va,x as ba,y as Ca,z as ka,B as xa}from"./vendor-arizeai-CsdcB1NH.js";import{u as wa}from"./pages-DnbxgoTK.js";import{V as Sa}from"./vendor-three-DwGkEfCM.js";import{j as Gn,E as Bn,l as Qn,a as Un,R as Ye,n as en,p as Ma}from"./vendor-codemirror-CYHkhs7D.js";const Ta=e=>{const t=a=>({markdownDisplayMode:"text",setMarkdownDisplayMode:r=>{a({markdownDisplayMode:r})},traceStreamingEnabled:!0,setTraceStreamingEnabled:r=>{a({traceStreamingEnabled:r})},showSpanAside:!0,setShowSpanAside:r=>{a({showSpanAside:r})},showMetricsInTraceTree:!0,setShowMetricsInTraceTree:r=>{a({showMetricsInTraceTree:r})},...e});return We()(Ft(Je(t),{name:"arize-phoenix-preferences"}))},Hn=p.createContext(null);function Gl({children:e,...t}){const a=p.useRef();return a.current||(a.current=Ta(t)),n(Hn.Provider,{value:a.current,children:e})}function be(e,t){const a=W.useContext(Hn);if(!a)throw new Error("Missing PreferencesContext.Provider in the tree");return Pn(a,e,t)}var G=(e=>(e.primary="primary",e.reference="reference",e.corpus="corpus",e))(G||{});function P(e){throw new Error("Unreachable")}function nn(e){return typeof e=="number"||e===null}function Ia(e){return typeof e=="string"||e===null}function Bl(e){return Array.isArray(e)?e.every(t=>typeof t=="string"):!1}function Da(e){return typeof e=="object"&&e!==null}const tn=p.createContext(null);function Oe(){const e=W.useContext(tn);if(e===null)throw new Error("useInferences must be used within a InferencesProvider");return e}function Ql(e){return n(tn.Provider,{value:{primaryInferences:e.primaryInferences,referenceInferences:e.referenceInferences,corpusInferences:e.corpusInferences,getInferencesNameByRole:t=>{var a,r;switch(t){case G.primary:return e.primaryInferences.name;case G.reference:return((a=e.referenceInferences)==null?void 0:a.name)??"reference";case G.corpus:return((r=e.corpusInferences)==null?void 0:r.name)??"corpus";default:P()}}},children:e.children})}const Zn=function(){var e={defaultValue:null,kind:"LocalArgument",name:"clusters"},t={defaultValue:null,kind:"LocalArgument",name:"dataQualityMetricColumnName"},a={defaultValue:null,kind:"LocalArgument",name:"fetchDataQualityMetric"},r={defaultValue:null,kind:"LocalArgument",name:"fetchPerformanceMetric"},i={defaultValue:null,kind:"LocalArgument",name:"performanceMetric"},l=[{alias:null,args:null,kind:"ScalarField",name:"primaryValue",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"referenceValue",storageKey:null}],o=[{alias:null,args:[{kind:"Variable",name:"clusters",variableName:"clusters"}],concreteType:"Cluster",kind:"LinkedField",name:"clusters",plural:!0,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"eventIds",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"driftRatio",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"primaryToCorpusRatio",storageKey:null},{condition:"fetchDataQualityMetric",kind:"Condition",passingValue:!0,selections:[{alias:null,args:[{fields:[{kind:"Variable",name:"columnName",variableName:"dataQualityMetricColumnName"},{kind:"Literal",name:"metric",value:"mean"}],kind:"ObjectValue",name:"metric"}],concreteType:"DatasetValues",kind:"LinkedField",name:"dataQualityMetric",plural:!1,selections:l,storageKey:null}]},{condition:"fetchPerformanceMetric",kind:"Condition",passingValue:!0,selections:[{alias:null,args:[{fields:[{kind:"Variable",name:"metric",variableName:"performanceMetric"}],kind:"ObjectValue",name:"metric"}],concreteType:"DatasetValues",kind:"LinkedField",name:"performanceMetric",plural:!1,selections:l,storageKey:null}]}],storageKey:null}];return{fragment:{argumentDefinitions:[e,t,a,r,i],kind:"Fragment",metadata:null,name:"pointCloudStore_clusterMetricsQuery",selections:o,type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[e,a,t,r,i],kind:"Operation",name:"pointCloudStore_clusterMetricsQuery",selections:o},params:{cacheID:"86666967012812887ac0a0149d2d2535",id:null,metadata:{},name:"pointCloudStore_clusterMetricsQuery",operationKind:"query",text:`query pointCloudStore_clusterMetricsQuery(
  $clusters: [ClusterInput!]!
  $fetchDataQualityMetric: Boolean!
  $dataQualityMetricColumnName: String
  $fetchPerformanceMetric: Boolean!
  $performanceMetric: PerformanceMetric!
) {
  clusters(clusters: $clusters) {
    id
    eventIds
    driftRatio
    primaryToCorpusRatio
    dataQualityMetric(metric: {metric: mean, columnName: $dataQualityMetricColumnName}) @include(if: $fetchDataQualityMetric) {
      primaryValue
      referenceValue
    }
    performanceMetric(metric: {metric: $performanceMetric}) @include(if: $fetchPerformanceMetric) {
      primaryValue
      referenceValue
    }
  }
}
`}}}();Zn.hash="dbfc8c02ba1ec4f2ba0317b371854d9b";const jn=function(){var e={defaultValue:null,kind:"LocalArgument",name:"clusterMinSamples"},t={defaultValue:null,kind:"LocalArgument",name:"clusterSelectionEpsilon"},a={defaultValue:null,kind:"LocalArgument",name:"coordinates"},r={defaultValue:null,kind:"LocalArgument",name:"dataQualityMetricColumnName"},i={defaultValue:null,kind:"LocalArgument",name:"eventIds"},l={defaultValue:null,kind:"LocalArgument",name:"fetchDataQualityMetric"},o={defaultValue:null,kind:"LocalArgument",name:"fetchPerformanceMetric"},d={defaultValue:null,kind:"LocalArgument",name:"minClusterSize"},c={defaultValue:null,kind:"LocalArgument",name:"performanceMetric"},u=[{alias:null,args:null,kind:"ScalarField",name:"primaryValue",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"referenceValue",storageKey:null}],h=[{alias:null,args:[{kind:"Variable",name:"clusterMinSamples",variableName:"clusterMinSamples"},{kind:"Variable",name:"clusterSelectionEpsilon",variableName:"clusterSelectionEpsilon"},{kind:"Variable",name:"coordinates3d",variableName:"coordinates"},{kind:"Variable",name:"eventIds",variableName:"eventIds"},{kind:"Variable",name:"minClusterSize",variableName:"minClusterSize"}],concreteType:"Cluster",kind:"LinkedField",name:"hdbscanClustering",plural:!0,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"eventIds",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"driftRatio",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"primaryToCorpusRatio",storageKey:null},{condition:"fetchDataQualityMetric",kind:"Condition",passingValue:!0,selections:[{alias:null,args:[{fields:[{kind:"Variable",name:"columnName",variableName:"dataQualityMetricColumnName"},{kind:"Literal",name:"metric",value:"mean"}],kind:"ObjectValue",name:"metric"}],concreteType:"DatasetValues",kind:"LinkedField",name:"dataQualityMetric",plural:!1,selections:u,storageKey:null}]},{condition:"fetchPerformanceMetric",kind:"Condition",passingValue:!0,selections:[{alias:null,args:[{fields:[{kind:"Variable",name:"metric",variableName:"performanceMetric"}],kind:"ObjectValue",name:"metric"}],concreteType:"DatasetValues",kind:"LinkedField",name:"performanceMetric",plural:!1,selections:u,storageKey:null}]}],storageKey:null}];return{fragment:{argumentDefinitions:[e,t,a,r,i,l,o,d,c],kind:"Fragment",metadata:null,name:"pointCloudStore_clustersQuery",selections:h,type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[i,a,d,e,t,l,r,o,c],kind:"Operation",name:"pointCloudStore_clustersQuery",selections:h},params:{cacheID:"a1a02d970d255935edfcdd797e4ca80d",id:null,metadata:{},name:"pointCloudStore_clustersQuery",operationKind:"query",text:`query pointCloudStore_clustersQuery(
  $eventIds: [ID!]!
  $coordinates: [InputCoordinate3D!]!
  $minClusterSize: Int!
  $clusterMinSamples: Int!
  $clusterSelectionEpsilon: Float!
  $fetchDataQualityMetric: Boolean!
  $dataQualityMetricColumnName: String
  $fetchPerformanceMetric: Boolean!
  $performanceMetric: PerformanceMetric!
) {
  hdbscanClustering(eventIds: $eventIds, coordinates3d: $coordinates, minClusterSize: $minClusterSize, clusterMinSamples: $clusterMinSamples, clusterSelectionEpsilon: $clusterSelectionEpsilon) {
    id
    eventIds
    driftRatio
    primaryToCorpusRatio
    dataQualityMetric(metric: {metric: mean, columnName: $dataQualityMetricColumnName}) @include(if: $fetchDataQualityMetric) {
      primaryValue
      referenceValue
    }
    performanceMetric(metric: {metric: $performanceMetric}) @include(if: $fetchPerformanceMetric) {
      primaryValue
      referenceValue
    }
  }
}
`}}}();jn.hash="b26f299a862a3bc4f5487ace49db1d43";const qn=function(){var e={defaultValue:null,kind:"LocalArgument",name:"corpusEventIds"},t={defaultValue:null,kind:"LocalArgument",name:"primaryEventIds"},a={defaultValue:null,kind:"LocalArgument",name:"referenceEventIds"},r={alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},i={alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},l={alias:null,args:null,kind:"ScalarField",name:"type",storageKey:null},o={alias:null,args:null,kind:"ScalarField",name:"value",storageKey:null},d={alias:null,args:null,concreteType:"EventMetadata",kind:"LinkedField",name:"eventMetadata",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"predictionId",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"predictionLabel",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"predictionScore",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"actualLabel",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"actualScore",storageKey:null}],storageKey:null},c={alias:null,args:null,concreteType:"PromptResponse",kind:"LinkedField",name:"promptAndResponse",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"prompt",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"response",storageKey:null}],storageKey:null},u={alias:null,args:null,kind:"ScalarField",name:"documentText",storageKey:null},h=[r,{alias:null,args:null,concreteType:"DimensionWithValue",kind:"LinkedField",name:"dimensions",plural:!0,selections:[{alias:null,args:null,concreteType:"Dimension",kind:"LinkedField",name:"dimension",plural:!1,selections:[i,l],storageKey:null},o],storageKey:null},d,c,u],g=[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:null,args:null,concreteType:"Inferences",kind:"LinkedField",name:"primaryInferences",plural:!1,selections:[{alias:null,args:[{kind:"Variable",name:"eventIds",variableName:"primaryEventIds"}],concreteType:"Event",kind:"LinkedField",name:"events",plural:!0,selections:h,storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"Inferences",kind:"LinkedField",name:"referenceInferences",plural:!1,selections:[{alias:null,args:[{kind:"Variable",name:"eventIds",variableName:"referenceEventIds"}],concreteType:"Event",kind:"LinkedField",name:"events",plural:!0,selections:[r,{alias:null,args:null,concreteType:"DimensionWithValue",kind:"LinkedField",name:"dimensions",plural:!0,selections:[{alias:null,args:null,concreteType:"Dimension",kind:"LinkedField",name:"dimension",plural:!1,selections:[r,i,l],storageKey:null},o],storageKey:null},d,c,u],storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"Inferences",kind:"LinkedField",name:"corpusInferences",plural:!1,selections:[{alias:null,args:[{kind:"Variable",name:"eventIds",variableName:"corpusEventIds"}],concreteType:"Event",kind:"LinkedField",name:"events",plural:!0,selections:h,storageKey:null}],storageKey:null}],storageKey:null}];return{fragment:{argumentDefinitions:[e,t,a],kind:"Fragment",metadata:null,name:"pointCloudStore_eventsQuery",selections:g,type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[t,a,e],kind:"Operation",name:"pointCloudStore_eventsQuery",selections:g},params:{cacheID:"388c28f19a685a131b1dfd4bac80cb7c",id:null,metadata:{},name:"pointCloudStore_eventsQuery",operationKind:"query",text:`query pointCloudStore_eventsQuery(
  $primaryEventIds: [ID!]!
  $referenceEventIds: [ID!]!
  $corpusEventIds: [ID!]!
) {
  model {
    primaryInferences {
      events(eventIds: $primaryEventIds) {
        id
        dimensions {
          dimension {
            name
            type
          }
          value
        }
        eventMetadata {
          predictionId
          predictionLabel
          predictionScore
          actualLabel
          actualScore
        }
        promptAndResponse {
          prompt
          response
        }
        documentText
      }
    }
    referenceInferences {
      events(eventIds: $referenceEventIds) {
        id
        dimensions {
          dimension {
            id
            name
            type
          }
          value
        }
        eventMetadata {
          predictionId
          predictionLabel
          predictionScore
          actualLabel
          actualScore
        }
        promptAndResponse {
          prompt
          response
        }
        documentText
      }
    }
    corpusInferences {
      events(eventIds: $corpusEventIds) {
        id
        dimensions {
          dimension {
            name
            type
          }
          value
        }
        eventMetadata {
          predictionId
          predictionLabel
          predictionScore
          actualLabel
          actualScore
        }
        promptAndResponse {
          prompt
          response
        }
        documentText
      }
    }
  }
}
`}}}();qn.hash="00a957322684d9186fdf16d33a75b931";const Wn=function(){var e={defaultValue:null,kind:"LocalArgument",name:"getDimensionCategories"},t={defaultValue:null,kind:"LocalArgument",name:"getDimensionMinMax"},a={defaultValue:null,kind:"LocalArgument",name:"id"},r=[{kind:"Variable",name:"id",variableName:"id"}],i={alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},l={condition:"getDimensionMinMax",kind:"Condition",passingValue:!0,selections:[{alias:"min",args:[{kind:"Literal",name:"metric",value:"min"}],kind:"ScalarField",name:"dataQualityMetric",storageKey:'dataQualityMetric(metric:"min")'},{alias:"max",args:[{kind:"Literal",name:"metric",value:"max"}],kind:"ScalarField",name:"dataQualityMetric",storageKey:'dataQualityMetric(metric:"max")'}]},o={condition:"getDimensionCategories",kind:"Condition",passingValue:!0,selections:[{alias:null,args:null,kind:"ScalarField",name:"categories",storageKey:null}]};return{fragment:{argumentDefinitions:[e,t,a],kind:"Fragment",metadata:null,name:"pointCloudStore_dimensionMetadataQuery",selections:[{kind:"RequiredField",field:{alias:"dimension",args:r,concreteType:null,kind:"LinkedField",name:"node",plural:!1,selections:[{kind:"InlineFragment",selections:[i,l,o],type:"Dimension",abstractKey:null}],storageKey:null},action:"THROW",path:"dimension"}],type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[a,t,e],kind:"Operation",name:"pointCloudStore_dimensionMetadataQuery",selections:[{alias:"dimension",args:r,concreteType:null,kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"__typename",storageKey:null},{kind:"TypeDiscriminator",abstractKey:"__isNode"},i,{kind:"InlineFragment",selections:[l,o],type:"Dimension",abstractKey:null}],storageKey:null}]},params:{cacheID:"79c15606d5694bd068270b42ed2fe74c",id:null,metadata:{},name:"pointCloudStore_dimensionMetadataQuery",operationKind:"query",text:`query pointCloudStore_dimensionMetadataQuery(
  $id: GlobalID!
  $getDimensionMinMax: Boolean!
  $getDimensionCategories: Boolean!
) {
  dimension: node(id: $id) {
    __typename
    ... on Dimension {
      id
      min: dataQualityMetric(metric: min) @include(if: $getDimensionMinMax)
      max: dataQualityMetric(metric: max) @include(if: $getDimensionMinMax)
      categories @include(if: $getDimensionCategories)
    }
    __isNode: __typename
    id
  }
}
`}}}();Wn.hash="e8fa488a0d466b5e40fdadc1e5227a57";const Ea=30,mn=5,pn=100,Fa=0,gn=0,hn=.99,_a=500,fn=300,Ln=1e5,Pa=10,yn=1,Va=2,Na=1,Ra=0;var M=(e=>(e.inferences="inferences",e.correctness="correctness",e.dimension="dimension",e))(M||{}),de=(e=>(e.list="list",e.gallery="gallery",e))(de||{}),ce=(e=>(e.small="small",e.medium="medium",e.large="large",e))(ce||{}),T=(e=>(e.primary="primary",e.reference="reference",e.corpus="corpus",e))(T||{}),E=(e=>(e.correct="correct",e.incorrect="incorrect",e.unknown="unknown",e))(E||{});const Oa=["#05fbff","#cb8afd"],Aa=["#00add0","#4500d9"],j="#a5a5a5",le=j;function Ka(e){return e.endsWith("/")?e.slice(0,-1):e}const za=`${window.location.protocol}//${window.location.host}${Ka(window.Config.basename)}`,Ul=window.Config.platformVersion,$a=za+"/graphql",Ga=async(e,t,a)=>{const i=await(await fetch($a,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e.text,variables:t})})).json();if(Array.isArray(i.errors))throw new Error(`Error fetching GraphQL query '${e.name}' with variables '${JSON.stringify(t)}': ${JSON.stringify(i.errors)}`);return i},Se=new Me.Environment({network:Me.Network.create(Ga),store:new Me.Store(new Me.RecordSource,{gcReleaseBufferSize:10})});function Jn(e){return e.includes("PRIMARY")?G.primary:e.includes("CORPUS")?G.corpus:G.reference}function an(e){const t=[],a=[],r=[];return e.forEach(i=>{const l=Jn(i);l==G.primary?t.push(i):l==G.corpus?r.push(i):a.push(i)}),{primaryEventIds:t,referenceEventIds:a,corpusEventIds:r}}const _e=10,ye="unknown",Xn=Pt,Yn=_t,Ba=e=>Yn[e],Qa=e=>Xn(e/_e);var ue=(e=>(e.move="move",e.select="select",e))(ue||{}),rn=(e=>(e.default="default",e.highlight="highlight",e))(rn||{});const oe=()=>it()==="light"?Aa:Oa;function Hl(){const e=oe();return{coloringStrategy:M.inferences,pointGroupVisibility:{[T.primary]:!0,[T.reference]:!0},pointGroupColors:{[T.primary]:e[0],[T.reference]:e[1],[T.corpus]:j},metric:{type:"drift",metric:"euclideanDistance"}}}function Zl(){const e=oe();return{coloringStrategy:M.inferences,pointGroupVisibility:{[T.primary]:!0,[T.corpus]:!0},pointGroupColors:{[T.primary]:e[0],[T.corpus]:j},metric:{type:"retrieval",metric:"queryDistance"},clusterSort:{dir:"desc",column:"primaryMetricValue"}}}function jl(){return{coloringStrategy:M.correctness,pointGroupVisibility:{[E.correct]:!0,[E.incorrect]:!0,[E.unknown]:!0},pointGroupColors:{[E.correct]:Fe.Discrete2.LightBlueOrange[0],[E.incorrect]:Fe.Discrete2.LightBlueOrange[1],[E.unknown]:le},metric:{type:"performance",metric:"accuracyScore"},clusterSort:{dir:"asc",column:"primaryMetricValue"}}}const Ua=e=>{const t={loading:!1,errorMessage:null,points:[],eventIdToDataMap:new Map,clusters:[],clusterSort:{dir:"desc",column:"driftRatio"},pointData:null,selectedEventIds:new Set,hoveredEventId:null,highlightedClusterId:null,selectedClusterId:null,canvasMode:"move",pointSizeScale:1,clusterColorMode:"default",coloringStrategy:M.inferences,inferencesVisibility:{primary:!0,reference:!0,corpus:!0},pointGroupVisibility:{[T.primary]:!0,[T.reference]:!0,[T.corpus]:!0},pointGroupColors:{[T.primary]:oe()[0],[T.reference]:oe()[1],[T.corpus]:j},eventIdToGroup:{},selectionDisplay:de.gallery,selectionGridSize:ce.large,dimension:null,dimensionMetadata:null,umapParameters:{minDist:Fa,nNeighbors:Ea,nSamples:_a},hdbscanParameters:{minClusterSize:Pa,clusterMinSamples:Na,clusterSelectionEpsilon:Ra},clustersLoading:!1,metric:{type:"drift",metric:"euclideanDistance"},selectionSearchText:""},a=(r,i)=>({...t,...e,setInitialData:async({points:l,clusters:o,retrievals:d})=>{const c=i(),u=new Map,h=d.reduce((L,y)=>{const{queryId:k}=y;return L[k]?L[k].push(y):L[k]=[y],L},{});l.forEach(L=>{L={...L,retrievals:h[L.eventId]??[]},u.set(L.eventId,L)});const g=o.map(bn).sort(Be(c.clusterSort));r({loading:!1,points:l,eventIdToDataMap:u,clusters:g,clustersLoading:!1,selectedEventIds:new Set,selectedClusterId:null,pointData:null,eventIdToGroup:te({points:l,coloringStrategy:c.coloringStrategy,pointsData:c.pointData??{},dimension:c.dimension||null,dimensionMetadata:c.dimensionMetadata})});const f=await ja(l.map(L=>L.eventId)).catch(()=>r({errorMessage:"Failed to load the point events"}));f&&r({pointData:f,clusters:g,clustersLoading:!1,eventIdToGroup:te({points:l,coloringStrategy:c.coloringStrategy,pointsData:f??{},dimension:c.dimension||null,dimensionMetadata:c.dimensionMetadata})})},setClusters:l=>{const o=i(),d=l.map(bn).sort(Be(o.clusterSort));r({clusters:d,clustersLoading:!1,selectedClusterId:null,highlightedClusterId:null})},setClusterSort:l=>{const d=[...i().clusters].sort(Be(l));r({clusterSort:l,clusters:d})},setSelectedEventIds:l=>r({selectedEventIds:l,selectionSearchText:""}),setHoveredEventId:l=>r({hoveredEventId:l}),setHighlightedClusterId:l=>r({highlightedClusterId:l}),setSelectedClusterId:l=>r({selectedClusterId:l,highlightedClusterId:null}),setPointSizeScale:l=>r({pointSizeScale:l}),setCanvasMode:l=>r({canvasMode:l}),setClusterColorMode:l=>r({clusterColorMode:l}),setColoringStrategy:l=>{const o=i();switch(r({coloringStrategy:l}),l){case M.correctness:r({pointGroupVisibility:{[E.correct]:!0,[E.incorrect]:!0,[E.unknown]:!0},pointGroupColors:{[E.correct]:Fe.Discrete2.LightBlueOrange[0],[E.incorrect]:Fe.Discrete2.LightBlueOrange[1],[E.unknown]:le},dimension:null,dimensionMetadata:null,eventIdToGroup:te({points:o.points,coloringStrategy:l,pointsData:o.pointData??{},dimension:o.dimension||null,dimensionMetadata:o.dimensionMetadata})});break;case M.inferences:{r({pointGroupVisibility:{[T.primary]:!0,[T.reference]:!0,[T.corpus]:!0},pointGroupColors:{[T.primary]:oe()[0],[T.reference]:oe()[1],[T.corpus]:j},dimension:null,dimensionMetadata:null,eventIdToGroup:te({points:o.points,coloringStrategy:l,pointsData:o.pointData??{},dimension:o.dimension||null,dimensionMetadata:o.dimensionMetadata})});break}case M.dimension:{r({pointGroupVisibility:{unknown:!0},pointGroupColors:{unknown:le},dimension:null,dimensionMetadata:null,eventIdToGroup:te({points:o.points,coloringStrategy:l,pointsData:o.pointData??{},dimension:o.dimension||null,dimensionMetadata:o.dimensionMetadata})});break}default:P()}},inferencesVisibility:{primary:!0,reference:!0,corpus:!0},setInferencesVisibility:l=>r({inferencesVisibility:l}),setPointGroupVisibility:l=>r({pointGroupVisibility:l}),selectionDisplay:de.gallery,setSelectionDisplay:l=>r({selectionDisplay:l}),setSelectionGridSize:l=>r({selectionGridSize:l}),reset:()=>{r({points:[],clusters:[],selectedEventIds:new Set,selectedClusterId:null,eventIdToGroup:{}})},setDimension:async l=>{const o=i();r({dimension:l,dimensionMetadata:null});const d=await Za(l).catch(()=>r({errorMessage:"Failed to load the dimension metadata"}));if(d){if(r({dimensionMetadata:d}),d.categories&&d.categories.length){const c=d.categories.length,h=c<=Yn.length?Ba:g=>Xn(g/c);r({pointGroupVisibility:{...d.categories.reduce((g,f)=>({...g,[f]:!0}),{}),unknown:!0},pointGroupColors:{...d.categories.reduce((g,f,L)=>({...g,[f]:h(L)}),{}),unknown:le},eventIdToGroup:te({points:o.points,coloringStrategy:o.coloringStrategy,pointsData:o.pointData??{},dimension:l,dimensionMetadata:d})})}else if(d.interval!==null){const c=et(d.interval);r({pointGroupVisibility:{...c.reduce((u,h)=>({...u,[h.name]:!0}),{}),unknown:!0},pointGroupColors:{...c.reduce((u,h,g)=>({...u,[h.name]:Qa(g)}),{}),unknown:le},eventIdToGroup:te({points:o.points,coloringStrategy:o.coloringStrategy,pointsData:o.pointData??{},dimension:l,dimensionMetadata:d})})}}},setDimensionMetadata:l=>r({dimensionMetadata:l}),setUMAPParameters:l=>r({umapParameters:l}),setHDBSCANParameters:async l=>{const o=i();r({hdbscanParameters:l,clustersLoading:!0});const d=await qa({metric:o.metric,points:o.points,hdbscanParameters:l});o.setClusters(d)},getHDSCANParameters:()=>i().hdbscanParameters,getMetric:()=>i().metric,setErrorMessage:l=>r({errorMessage:l}),setLoading:l=>r({loading:l}),setMetric:async l=>{const o=i();r({metric:l,clustersLoading:!0});const d=await Wa({metric:l,clusters:o.clusters,hdbscanParameters:o.hdbscanParameters});o.setClusters(d)},setSelectionSearchText:l=>r({selectionSearchText:l})});return We()(Je(a))},vn=new Intl.NumberFormat([],{maximumFractionDigits:2});function Ha({min:e,max:t}){return`${vn.format(e)} - ${vn.format(t)}`}function et({min:e,max:t}){const r=(t-e)/_e,i=[];for(let l=0;l<_e;l++){const o=e+l*r,d=e+(l+1)*r;i.push({min:o,max:d,name:Ha({min:o,max:d})})}return i}function Ge({numericGroupIntervals:e,numericValue:t}){let a=ye,r=e.findIndex(i=>t>=i.min&&t<i.max);return r=r===-1?_e-1:r,a=e[r].name,a}function te(e){const{points:t,coloringStrategy:a,pointsData:r,dimension:i,dimensionMetadata:l}=e,o={},d=t.map(c=>c.eventId);switch(a){case M.inferences:{const{primaryEventIds:c,referenceEventIds:u,corpusEventIds:h}=an(d);c.forEach(g=>{o[g]=T.primary}),u.forEach(g=>{o[g]=T.reference}),h.forEach(g=>{o[g]=T.corpus});break}case M.correctness:{t.forEach(c=>{let u=E.unknown;const{predictionLabel:h,actualLabel:g}=c.eventMetadata;h!==null&&g!==null&&(u=h===g?E.correct:E.incorrect),o[c.eventId]=u});break}case M.dimension:{let c;l&&(l==null?void 0:l.interval)!==null&&(c=et(l.interval));const u=(i==null?void 0:i.type)==="prediction"&&(i==null?void 0:i.dataType)==="categorical",h=(i==null?void 0:i.type)==="prediction"&&(i==null?void 0:i.dataType)==="numeric",g=(i==null?void 0:i.type)==="actual"&&(i==null?void 0:i.dataType)==="categorical",f=(i==null?void 0:i.type)==="actual"&&(i==null?void 0:i.dataType)==="numeric";t.forEach(L=>{let y=ye;const k=r[L.eventId];if(i!=null&&k!=null)if(u)y=k.eventMetadata.predictionLabel??ye;else if(h){if(c==null)throw new Error("Cannot color by prediction score without numeric group intervals");const x=k.eventMetadata.predictionScore;typeof x=="number"&&(y=Ge({numericGroupIntervals:c,numericValue:x}))}else if(f){if(c==null)throw new Error("Cannot color by actual score without numeric group intervals");const x=k.eventMetadata.actualScore;typeof x=="number"&&(y=Ge({numericGroupIntervals:c,numericValue:x}))}else if(g)y=k.eventMetadata.actualLabel??ye;else{const x=k.dimensions.find(F=>F.dimension.name===i.name);if(x!=null&&i.dataType==="categorical")y=x.value??ye;else if(x!=null&&i.dataType==="numeric"&&c!=null){const F=typeof(x==null?void 0:x.value)=="string"?parseFloat(x.value):null;typeof F=="number"&&(y=Ge({numericGroupIntervals:c,numericValue:F}))}}o[L.eventId]=y});break}default:P()}return o}async function Za(e){const t=await Z.fetchQuery(Se,Wn,{id:e.id,getDimensionMinMax:e.dataType==="numeric",getDimensionCategories:e.dataType==="categorical"}).toPromise(),a=t==null?void 0:t.dimension;if(!e)throw new Error("Dimension not found");let r=null;return typeof(a==null?void 0:a.min)=="number"&&typeof(a==null?void 0:a.max)=="number"&&(r={min:a.min,max:a.max}),{interval:r,categories:(a==null?void 0:a.categories)??null}}async function ja(e){var u,h,g,f,L,y;const{primaryEventIds:t,referenceEventIds:a,corpusEventIds:r}=an([...e]),i=await Z.fetchQuery(Se,qn,{primaryEventIds:t,referenceEventIds:a,corpusEventIds:r}).toPromise(),l=((h=(u=i==null?void 0:i.model)==null?void 0:u.primaryInferences)==null?void 0:h.events)??[],o=((f=(g=i==null?void 0:i.model)==null?void 0:g.referenceInferences)==null?void 0:f.events)??[],d=((y=(L=i==null?void 0:i.model)==null?void 0:L.corpusInferences)==null?void 0:y.events)??[];return[...l,...o,...d].reduce((k,V)=>(k[V.id]=V,k),{})}async function qa({metric:e,points:t,hdbscanParameters:a}){const r=await Z.fetchQuery(Se,jn,{eventIds:t.map(i=>i.eventId),coordinates:t.map(i=>({x:i.position[0],y:i.position[1],z:i.position[2]})),fetchDataQualityMetric:e.type==="dataQuality",dataQualityMetricColumnName:e.type==="dataQuality"?e.dimension.name:null,fetchPerformanceMetric:e.type==="performance",performanceMetric:e.type==="performance"?e.metric:"accuracyScore",...a},{fetchPolicy:"network-only"}).toPromise();return(r==null?void 0:r.hdbscanClustering)??[]}async function Wa({metric:e,clusters:t,hdbscanParameters:a}){const r=await Z.fetchQuery(Se,Zn,{clusters:t.map(i=>({id:i.id,eventIds:i.eventIds})),fetchDataQualityMetric:e.type==="dataQuality",dataQualityMetricColumnName:e.type==="dataQuality"?e.dimension.name:null,fetchPerformanceMetric:e.type==="performance",performanceMetric:e.type==="performance"?e.metric:"accuracyScore",...a},{fetchPolicy:"network-only"}).toPromise();return(r==null?void 0:r.clusters)??[]}const Be=e=>(t,a)=>{const{dir:r,column:i}=e,l=r==="asc",o=t[i],d=a[i];return o==null?1:d==null?-1:o>d?l?1:-1:o<d?l?-1:1:0};function bn(e){let t=e.driftRatio,a=null;return e.dataQualityMetric?(t=e.dataQualityMetric.primaryValue,a=e.dataQualityMetric.referenceValue):e.performanceMetric?(t=e.performanceMetric.primaryValue,a=e.performanceMetric.referenceValue):e.primaryToCorpusRatio!=null&&(t=(e.primaryToCorpusRatio+1)/2*100),{...e,size:e.eventIds.length,primaryMetricValue:t,referenceMetricValue:a}}const ln=p.createContext(null);function ql({children:e,...t}){const a=p.useRef();return a.current||(a.current=Ua(t)),n(ln.Provider,{value:a.current,children:e})}function v(e,t){const a=p.useContext(ln);if(!a)throw new Error("Missing PointCloudContext.Provider in the tree");return Pn(a,e,t)}var z=(e=>(e.last_hour="Last Hour",e.last_day="Last Day",e.last_week="Last Week",e.last_month="Last Month",e.last_3_months="Last 3 Months",e.first_hour="First Hour",e.first_day="First Day",e.first_week="First Week",e.first_month="First Month",e.all="All",e))(z||{});const nt=p.createContext(null);function Ja(){const e=p.useContext(nt);if(e===null)throw new Error("useTimeRange must be used within a TimeRangeProvider");return e}function Xa(e,t){return p.useMemo(()=>{switch(e){case"Last Hour":{const r=ie(Ot(t.end),{roundingMethod:"ceil"});return{start:At(r,1),end:r}}case"Last Day":{const r=ie(Rt(t.end),{roundingMethod:"ceil"});return{start:ae(r,1),end:r}}case"Last Week":{const r=ie(Te(t.end),{roundingMethod:"ceil"});return{start:ae(r,7),end:r}}case"Last Month":{const r=ie(Te(t.end),{roundingMethod:"ceil"});return{start:ae(r,30),end:r}}case"Last 3 Months":{const r=ie(Te(t.end),{roundingMethod:"ceil"});return{start:ae(r,90),end:r}}case"First Hour":{const r=Vt(t.start);return{start:r,end:Nt(r,1)}}case"First Day":{const r=Le(t.start);return{start:r,end:De(r,1)}}case"First Week":{const r=ze(t.start);return{start:r,end:De(r,7)}}case"First Month":{const r=ze(t.start);return{start:r,end:De(r,30)}}case"All":{const r=ie(Te(t.end),{roundingMethod:"floor"});return{start:ze(t.start),end:r}}default:P()}},[e,t])}function Wl(e){const[t,a]=p.useState("Last Month"),r=Xa(t,e.timeRangeBounds),i=p.useCallback(l=>{p.startTransition(()=>{a(l)})},[]);return n(nt.Provider,{value:{timeRange:r,timePreset:t,setTimePreset:i},children:e.children})}const tt=p.createContext(null);function Jl({children:e}){const[t,a]=da({style:{zIndex:1e3}}),r=p.useCallback(l=>{t({variant:"danger",...l})},[t]),i=p.useCallback(l=>{t({variant:"success",...l})},[t]);return s(tt.Provider,{value:{notify:t,notifyError:r,notifySuccess:i},children:[e,a]})}function at(){const e=p.useContext(tt);if(e===null)throw new Error("useGlobalNotification must be used within a NotificationProvider");return e}function Xl(){return at().notifyError}function Yl(){return at().notifySuccess}const rt="arize-phoenix-theme";function it(){return localStorage.getItem(rt)==="light"?"light":"dark"}const on=p.createContext(null);function U(){const e=p.useContext(on);if(e===null)throw new Error("useTheme must be used within a ThemeProvider");return e}function e1(e){const[t,a]=p.useState(it()),r=p.useCallback(i=>{localStorage.setItem(rt,i),a(i)},[]);return n(on.Provider,{value:{theme:t,setTheme:r},children:e.children})}function n1(e){return s("div",{role:"toolbar",css:m`
        padding: var(--px-spacing-sm) var(--px-spacing-lg);
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        gap: var(--px-spacing-med);
        border-bottom: 1px solid var(--ac-global-border-color-dark);
        flex: none;
        min-height: 29px;
        .toolbar__main {
          display: flex;
          flex-direction: row;
          gap: var(--px-spacing-med);
        }
      `,children:[n("div",{"data-testid":"toolbar-main",className:"toolbar__main",children:e.children}),e.extra?n("div",{"data-testid":"toolbar-extra",children:e.extra}):null]})}const je=Pe("%x %H:%M:%S %p");Pe("%H:%M %p");function t1(e){const{timeRange:t,timePreset:a,setTimePreset:r}=Ja(),{primaryInferences:{name:i}}=Oe(),l=i.slice(0,10);return n(An,{color:"designationTurquoise",children:s(A,{delay:0,placement:"bottom right",children:[n(q,{children:s(xe,{label:"primary inferences",defaultSelectedKey:a,"data-testid":"inferences-time-range","aria-label":"Time range for the primary inferences",addonBefore:l,onSelectionChange:o=>{o!==a&&r(o)},children:[n(_,{children:"All"},z.all),n(_,{children:"Last Hour"},z.last_hour),n(_,{children:"Last Day"},z.last_day),n(_,{children:"Last Week"},z.last_week),n(_,{children:"Last Month"},z.last_month),n(_,{children:"Last 3 Months"},z.last_3_months),n(_,{children:"First Hour"},z.first_hour),n(_,{children:"First Day"},z.first_day),n(_,{children:"First Week"},z.first_week),n(_,{children:"First Month"},z.first_month)]})}),n(Q,{children:s("section",{css:m`
              h4 {
                margin-bottom: 0.5rem;
              }
            `,children:[n(O,{level:4,children:"primary inferences time range"}),s("div",{children:["start: ",je(t.start)]}),s("div",{children:["end: ",je(t.end)]})]})})]})})}const Cn=Pe("%x %X");function a1({timeRange:e}){const{referenceInferences:t}=Oe(),r=((t==null?void 0:t.name)??"reference").slice(0,10);return n("div",{css:m`
        .ac-textfield {
          min-width: 371px;
        }
      `,children:n(An,{color:"designationPurple",children:s(A,{children:[n(q,{children:n($,{label:"reference inferences",isReadOnly:!0,"aria-label":"reference inferences time range",value:`${Cn(e.start)} - ${Cn(e.end)}`,addonBefore:r})}),n(Q,{children:"The static time range of the reference inferences"})]})})})}const lt=function(){var e=[{defaultValue:50,kind:"LocalArgument",name:"count"},{defaultValue:null,kind:"LocalArgument",name:"cursor"},{defaultValue:null,kind:"LocalArgument",name:"endTime"},{defaultValue:null,kind:"LocalArgument",name:"startTime"}],t=[{kind:"Variable",name:"after",variableName:"cursor"},{kind:"Variable",name:"first",variableName:"count"}],a={fields:[{kind:"Variable",name:"end",variableName:"endTime"},{kind:"Variable",name:"start",variableName:"startTime"}],kind:"ObjectValue",name:"timeRange"};return{fragment:{argumentDefinitions:e,kind:"Fragment",metadata:null,name:"ModelSchemaTableDimensionsQuery",selections:[{args:[{kind:"Variable",name:"count",variableName:"count"},{kind:"Variable",name:"cursor",variableName:"cursor"},{kind:"Variable",name:"endTime",variableName:"endTime"},{kind:"Variable",name:"startTime",variableName:"startTime"}],kind:"FragmentSpread",name:"ModelSchemaTable_dimensions"}],type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:e,kind:"Operation",name:"ModelSchemaTableDimensionsQuery",selections:[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:null,args:t,concreteType:"DimensionConnection",kind:"LinkedField",name:"dimensions",plural:!1,selections:[{alias:null,args:null,concreteType:"DimensionEdge",kind:"LinkedField",name:"edges",plural:!0,selections:[{alias:"dimension",args:null,concreteType:"Dimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"type",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"dataType",storageKey:null},{alias:"cardinality",args:[{kind:"Literal",name:"metric",value:"cardinality"},a],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"percentEmpty",args:[{kind:"Literal",name:"metric",value:"percentEmpty"},a],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"min",args:[{kind:"Literal",name:"metric",value:"min"},a],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"mean",args:[{kind:"Literal",name:"metric",value:"mean"},a],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"max",args:[{kind:"Literal",name:"metric",value:"max"},a],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"psi",args:[{kind:"Literal",name:"metric",value:"psi"},a],kind:"ScalarField",name:"driftMetric",storageKey:null}],storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"cursor",storageKey:null},{alias:null,args:null,concreteType:"Dimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"__typename",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"PageInfo",kind:"LinkedField",name:"pageInfo",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"endCursor",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"hasNextPage",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:t,filters:null,handle:"connection",key:"ModelSchemaTable_dimensions",kind:"LinkedHandle",name:"dimensions"}],storageKey:null}]},params:{cacheID:"0f5ec2a75c6234eefab01cbd1181c564",id:null,metadata:{},name:"ModelSchemaTableDimensionsQuery",operationKind:"query",text:`query ModelSchemaTableDimensionsQuery(
  $count: Int = 50
  $cursor: String = null
  $endTime: DateTime!
  $startTime: DateTime!
) {
  ...ModelSchemaTable_dimensions_4sIU9C
}

fragment ModelSchemaTable_dimensions_4sIU9C on Query {
  model {
    dimensions(first: $count, after: $cursor) {
      edges {
        dimension: node {
          id
          name
          type
          dataType
          cardinality: dataQualityMetric(metric: cardinality, timeRange: {start: $startTime, end: $endTime})
          percentEmpty: dataQualityMetric(metric: percentEmpty, timeRange: {start: $startTime, end: $endTime})
          min: dataQualityMetric(metric: min, timeRange: {start: $startTime, end: $endTime})
          mean: dataQualityMetric(metric: mean, timeRange: {start: $startTime, end: $endTime})
          max: dataQualityMetric(metric: max, timeRange: {start: $startTime, end: $endTime})
          psi: driftMetric(metric: psi, timeRange: {start: $startTime, end: $endTime})
        }
        cursor
        node {
          __typename
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
`}}}();lt.hash="fb4c57e0ea77548c4e96ceb418e06614";const ot=function(){var e=["model","dimensions"],t={fields:[{kind:"Variable",name:"end",variableName:"endTime"},{kind:"Variable",name:"start",variableName:"startTime"}],kind:"ObjectValue",name:"timeRange"};return{argumentDefinitions:[{defaultValue:50,kind:"LocalArgument",name:"count"},{defaultValue:null,kind:"LocalArgument",name:"cursor"},{defaultValue:null,kind:"LocalArgument",name:"endTime"},{defaultValue:null,kind:"LocalArgument",name:"startTime"}],kind:"Fragment",metadata:{connection:[{count:"count",cursor:"cursor",direction:"forward",path:e}],refetch:{connection:{forward:{count:"count",cursor:"cursor"},backward:null,path:e},fragmentPathInResult:[],operation:lt}},name:"ModelSchemaTable_dimensions",selections:[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:"dimensions",args:null,concreteType:"DimensionConnection",kind:"LinkedField",name:"__ModelSchemaTable_dimensions_connection",plural:!1,selections:[{alias:null,args:null,concreteType:"DimensionEdge",kind:"LinkedField",name:"edges",plural:!0,selections:[{alias:"dimension",args:null,concreteType:"Dimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"type",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"dataType",storageKey:null},{alias:"cardinality",args:[{kind:"Literal",name:"metric",value:"cardinality"},t],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"percentEmpty",args:[{kind:"Literal",name:"metric",value:"percentEmpty"},t],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"min",args:[{kind:"Literal",name:"metric",value:"min"},t],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"mean",args:[{kind:"Literal",name:"metric",value:"mean"},t],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"max",args:[{kind:"Literal",name:"metric",value:"max"},t],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"psi",args:[{kind:"Literal",name:"metric",value:"psi"},t],kind:"ScalarField",name:"driftMetric",storageKey:null}],storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"cursor",storageKey:null},{alias:null,args:null,concreteType:"Dimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"__typename",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"PageInfo",kind:"LinkedField",name:"pageInfo",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"endCursor",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"hasNextPage",storageKey:null}],storageKey:null}],storageKey:null}],storageKey:null}],type:"Query",abstractKey:null}}();ot.hash="fb4c57e0ea77548c4e96ceb418e06614";function st(e){return n("div",{onClick:t=>t.stopPropagation(),css:m`
        display: inline-block;
      `,children:n(Vn,{css:m`
          color: var(--ac-global-color-primary);
          &:not(:hover) {
            text-decoration: none;
          }
        `,...e})})}const ct=e=>m`
  font-size: ${e.typography.sizes.medium.fontSize}px;
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  thead {
    position: sticky;
    top: 0;
    z-index: 1;
    tr {
      th {
        padding: ${e.spacing.margin4}px ${e.spacing.margin16}px;
        background-color: var(--ac-global-color-grey-100);
        position: relative;
        text-align: left;
        user-select: none;
        border-bottom: 1px solid var(--ac-global-border-color-default);
        &:not(:last-of-type) {
          border-right: 1px solid var(--ac-global-border-color-default);
        }
        .cursor-pointer {
          cursor: pointer;
        }
        .sort-icon {
          margin-left: ${e.spacing.margin4}px;
          font-size: ${e.typography.sizes.small.fontSize}px;
          vertical-align: middle;
          display: inline-block;
        }
        &:hover .resizer {
          background: var(--ac-global-color-grey-300);
        }
        div.resizer {
          display: inline-block;

          width: 2px;
          height: 100%;
          position: absolute;
          right: 0;
          top: 0;
          cursor: grab;
          z-index: 4;
          touch-action: none;
          &.isResizing,
          &:hover {
            background: var(--ac-global-color-primary);
          }
        }
      }
    }
  }
  tbody:not(.is-empty) {
    tr {
      &:not(:last-of-type) {
        & > td {
          border-bottom: 1px solid var(--ac-global-border-color-default);
        }
      }
      &:hover {
        background-color: rgba(var(--ac-global-color-grey-300-rgb), 0.3);
      }
      & > td {
        padding: ${e.spacing.margin8}px ${e.spacing.margin16}px;
      }
    }
  }
`,r1=m`
  tbody:not(.is-empty) {
    tr {
      &:not(:last-of-type) {
        & > td {
          border-bottom: 1px solid var(--ac-global-border-color-default);
        }
      }
      & > td:not(:last-of-type) {
        border-right: 1px solid var(--ac-global-border-color-default);
      }
    }
  }
`,i1=e=>m(ct(e),m`
      tbody:not(.is-empty) {
        tr {
          cursor: pointer;
        }
      }
    `),Ya=e=>m`
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: ${e.spacing.margin8}px;
  gap: ${e.spacing.margin4}px;
  border-top: 1px solid var(--ac-global-color-grey-300);
`;function er(e){const{message:t="No Data"}=e;return n("tbody",{className:"is-empty",children:n("tr",{children:n("td",{colSpan:100,css:a=>m`
            text-align: center;
            padding: ${a.spacing.margin24}px ${a.spacing.margin24}px !important;
          `,children:t})})})}function dt({columns:e,data:t}){const a=Kt({columns:e,data:t,getCoreRowModel:zt(),getPaginationRowModel:$t(),getSortedRowModel:Gt()}),r=a.getRowModel().rows,l=r.length>0?n("tbody",{children:r.map(o=>n("tr",{children:o.getVisibleCells().map(d=>n("td",{children:dn(d.column.columnDef.cell,d.getContext())},d.id))},o.id))}):n(er,{});return s(Ve,{children:[s("table",{css:ct,children:[n("thead",{children:a.getHeaderGroups().map(o=>n("tr",{children:o.headers.map(d=>n("th",{colSpan:d.colSpan,children:d.isPlaceholder?null:n("div",{children:dn(d.column.columnDef.header,d.getContext())})},d.id))},o.id))}),l]}),s("div",{css:Ya,children:[n(B,{variant:"default",size:"compact",onClick:a.previousPage,disabled:!a.getCanPreviousPage(),"aria-label":"Previous Page",icon:n(I,{svg:n(w.ArrowIosBackOutline,{})})}),n(B,{variant:"default",size:"compact",onClick:a.nextPage,disabled:!a.getCanNextPage(),"aria-label":"Next Page",icon:n(I,{svg:n(w.ArrowIosForwardOutline,{})})})]})]})}function ut(e){return Math.abs(e)<1e6?se(",")(e):se("0.2s")(e)}function me(e){const t=Math.abs(e);return t===0?"0.00":t<.01?se(".2e")(e):t<1e3?se("0.2f")(e):se("0.2s")(e)}function nr(e){return se(".2f")(e)+"%"}function qe(e){return Number.isInteger(e)?ut(e):me(e)}function Ae(e){return t=>typeof t!="number"?"--":e(t)}const tr=Ae(ut),mt=Ae(me),kn=Ae(qe),ar=Ae(nr);function ve({getValue:e}){const t=e();if(!nn(t))throw new Error("IntCell only supports number or null values.");return n("span",{title:t!=null?String(t):"",children:mt(t)})}const rr=m`
  float: right;
`;function ir({getValue:e}){const t=e();if(!nn(t))throw new Error("IntCell only supports number or null values.");return n("span",{title:t!=null?String(t):"",css:rr,children:tr(t)})}function lr({getValue:e}){const t=e();if(!nn(t))throw new Error("IntCell only supports number or null values.");return n("span",{title:t!=null?String(t):"",children:ar(t)})}const xn=100;function or(e){return e.length>xn?`${e.slice(0,xn)}...`:e}function l1({getValue:e}){const t=e(),a=t!=null&&typeof t=="string"?or(t):"--";return n("span",{title:String(t),children:a})}function o1({getValue:e}){const t=e(),a=t!=null&&typeof t=="string"?t:"--";return n("pre",{style:{whiteSpace:"pre-wrap"},children:a})}const sr=m`
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
`;function wn(e,t){return e.length>t?`${e.slice(0,t)}...`:e}function cr({json:e,maxLength:t,space:a=0,disableTitle:r=!1}){const i=typeof t=="number",l=p.useMemo(()=>JSON.stringify(e,null,a),[e,a]),o=p.useMemo(()=>JSON.stringify(e,null,2),[e]),d=r?void 0:o;if(!Da(e))return console.warn("JSONText component received a non-object value",e),n("span",{title:d,children:String(e)});const c=e;if(Object.keys(c).length===0)return n("span",{title:d,children:"--"});if(Object.keys(c).length===1){const f=Object.keys(c)[0],L=c[f];if(typeof L=="string"){const y=i?wn(L,t):L;return n("span",{title:d,children:y})}}const u=i?wn(l,t):l;return n(i?"span":"pre",{title:d,css:i?void 0:sr,children:u})}const dr=100;function s1({getValue:e}){const t=e();return n(cr,{json:t,maxLength:dr})}function c1(e){const{data:t}=Z.usePaginationFragment(ot,e.model),a=p.useMemo(()=>t.model.dimensions.edges.map(({dimension:i})=>({...i})),[t]),r=W.useMemo(()=>[{header:"name",accessorKey:"name",cell:l=>n(st,{to:`dimensions/${l.row.original.id}`,children:l.renderValue()})},{header:"type",accessorKey:"type"},{header:"data type",accessorKey:"dataType"},{header:"cardinality",accessorKey:"cardinality",cell:ir},{header:"% empty",accessorKey:"percentEmpty",cell:lr},{header:"min",accessorKey:"min",cell:ve},{header:"mean",accessorKey:"mean",cell:ve},{header:"max",accessorKey:"max",cell:ve},{header:"PSI",accessorKey:"psi",cell:ve}],[]);return n(dt,{columns:r,data:a})}const pt=function(){var e=[{defaultValue:50,kind:"LocalArgument",name:"count"},{defaultValue:null,kind:"LocalArgument",name:"cursor"},{defaultValue:null,kind:"LocalArgument",name:"endTime"},{defaultValue:null,kind:"LocalArgument",name:"startTime"}],t=[{kind:"Variable",name:"after",variableName:"cursor"},{kind:"Variable",name:"first",variableName:"count"}];return{fragment:{argumentDefinitions:e,kind:"Fragment",metadata:null,name:"ModelEmbeddingsTableEmbeddingDimensionsQuery",selections:[{args:[{kind:"Variable",name:"count",variableName:"count"},{kind:"Variable",name:"cursor",variableName:"cursor"},{kind:"Variable",name:"endTime",variableName:"endTime"},{kind:"Variable",name:"startTime",variableName:"startTime"}],kind:"FragmentSpread",name:"ModelEmbeddingsTable_embeddingDimensions"}],type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:e,kind:"Operation",name:"ModelEmbeddingsTableEmbeddingDimensionsQuery",selections:[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:null,args:t,concreteType:"EmbeddingDimensionConnection",kind:"LinkedField",name:"embeddingDimensions",plural:!1,selections:[{alias:null,args:null,concreteType:"EmbeddingDimensionEdge",kind:"LinkedField",name:"edges",plural:!0,selections:[{alias:"embedding",args:null,concreteType:"EmbeddingDimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:"euclideanDistance",args:[{kind:"Literal",name:"metric",value:"euclideanDistance"},{fields:[{kind:"Variable",name:"end",variableName:"endTime"},{kind:"Variable",name:"start",variableName:"startTime"}],kind:"ObjectValue",name:"timeRange"}],kind:"ScalarField",name:"driftMetric",storageKey:null}],storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"cursor",storageKey:null},{alias:null,args:null,concreteType:"EmbeddingDimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"__typename",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"PageInfo",kind:"LinkedField",name:"pageInfo",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"endCursor",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"hasNextPage",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:t,filters:null,handle:"connection",key:"ModelEmbeddingsTable_embeddingDimensions",kind:"LinkedHandle",name:"embeddingDimensions"}],storageKey:null}]},params:{cacheID:"d0057a41a1d9795383a58de89e72ad76",id:null,metadata:{},name:"ModelEmbeddingsTableEmbeddingDimensionsQuery",operationKind:"query",text:`query ModelEmbeddingsTableEmbeddingDimensionsQuery(
  $count: Int = 50
  $cursor: String = null
  $endTime: DateTime!
  $startTime: DateTime!
) {
  ...ModelEmbeddingsTable_embeddingDimensions_4sIU9C
}

fragment ModelEmbeddingsTable_embeddingDimensions_4sIU9C on Query {
  model {
    embeddingDimensions(first: $count, after: $cursor) {
      edges {
        embedding: node {
          id
          name
          euclideanDistance: driftMetric(metric: euclideanDistance, timeRange: {start: $startTime, end: $endTime})
        }
        cursor
        node {
          __typename
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
`}}}();pt.hash="fb7f125f75d1d33a555c16e198dbcbf8";const gt=function(){var e=["model","embeddingDimensions"];return{argumentDefinitions:[{defaultValue:50,kind:"LocalArgument",name:"count"},{defaultValue:null,kind:"LocalArgument",name:"cursor"},{defaultValue:null,kind:"LocalArgument",name:"endTime"},{defaultValue:null,kind:"LocalArgument",name:"startTime"}],kind:"Fragment",metadata:{connection:[{count:"count",cursor:"cursor",direction:"forward",path:e}],refetch:{connection:{forward:{count:"count",cursor:"cursor"},backward:null,path:e},fragmentPathInResult:[],operation:pt}},name:"ModelEmbeddingsTable_embeddingDimensions",selections:[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:"embeddingDimensions",args:null,concreteType:"EmbeddingDimensionConnection",kind:"LinkedField",name:"__ModelEmbeddingsTable_embeddingDimensions_connection",plural:!1,selections:[{alias:null,args:null,concreteType:"EmbeddingDimensionEdge",kind:"LinkedField",name:"edges",plural:!0,selections:[{alias:"embedding",args:null,concreteType:"EmbeddingDimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:"euclideanDistance",args:[{kind:"Literal",name:"metric",value:"euclideanDistance"},{fields:[{kind:"Variable",name:"end",variableName:"endTime"},{kind:"Variable",name:"start",variableName:"startTime"}],kind:"ObjectValue",name:"timeRange"}],kind:"ScalarField",name:"driftMetric",storageKey:null}],storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"cursor",storageKey:null},{alias:null,args:null,concreteType:"EmbeddingDimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"__typename",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"PageInfo",kind:"LinkedField",name:"pageInfo",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"endCursor",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"hasNextPage",storageKey:null}],storageKey:null}],storageKey:null}],storageKey:null}],type:"Query",abstractKey:null}}();gt.hash="fb7f125f75d1d33a555c16e198dbcbf8";const ur=m`
  display: inline-flex;
  align-items: center;
  background: none;
  color: var(--ac-global-color-primary);
  border: none;
  padding: 0;
  font: inherit;
  cursor: pointer;
  outline: inherit;
  &:hover {
    text-decoration: underline;
  }
`;function d1(e){const{children:t,onClick:a}=e;return s("button",{css:ur,onClick:a,children:[t," ",n(I,{svg:n(ua,{})})]})}function pe({href:e,children:t}){return s("a",{href:e,target:"_blank",css:m`
        color: var(--ac-global-color-primary);
        text-decoration: none;
        display: flex;
        flex-direction: row;
        align-items: end;
        gap: var(--px-spacing-sm);
        &:hover {
          text-decoration: underline;
        }
        .ac-icon-wrap {
          font-size: 1em;
        }
      `,rel:"noreferrer",children:[t,n(I,{svg:n(w.ExternalLinkOutline,{})})]})}const u1=()=>n("div",{css:m`
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: rgba(0, 0, 0, 0.2);
      `,children:n(Kn,{isIndeterminate:!0,"aria-label":"loading"})}),mr=({message:e})=>s("div",{css:m`
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: 100%;
        gap: var(--px-spacing-med);
      `,children:[n(Kn,{isIndeterminate:!0,"aria-label":"loading"}),e!=null?n(C,{children:e}):null]});function m1(e){const{width:t="size-1250"}=e;return n(R,{width:t,backgroundColor:"light",borderStartWidth:"thin",borderStartColor:"dark",padding:"size-200",flex:"none",children:n(D,{direction:"column",alignItems:"end",justifyContent:"center",height:"100%",children:e.children})})}const pr=2e3;function gr({text:e,size:t="compact",disabled:a=!1}){const[r,i]=p.useState(!1),l=p.useCallback(()=>{Bt(e),i(!0),setTimeout(()=>{i(!1)},pr)},[e]);return n("div",{className:"copy-to-clipboard-button",children:s(A,{delay:0,offset:5,children:[n(B,{variant:"default",disabled:a,icon:n(I,{svg:r?n(w.Checkmark,{}):n(w.ClipboardCopy,{})}),size:t,onClick:l}),n(Q,{children:"Copy"})]})})}function p1(e){const{data:t}=Z.usePaginationFragment(gt,e.model),a=p.useMemo(()=>t.model.embeddingDimensions.edges.map(({embedding:i})=>({...i})),[t]),r=W.useMemo(()=>[{header:"name",accessorKey:"name",cell:({row:l,renderValue:o})=>n(st,{to:`embeddings/${l.original.id}`,children:o()})},{header:"euclidean distance",accessorKey:"euclideanDistance",cell:ve}],[]);return n(dt,{columns:r,data:a})}const ht=p.createContext(null),hr=()=>{const e=p.useContext(ht);if(e===null)throw new Error("useTimeSlice must be used within a TimeSliceProvider");return e},g1=({initialTimestamp:e,children:t})=>{const[a,r]=p.useState(e),i=l=>{p.startTransition(()=>{r(l)})};return n(ht.Provider,{value:{selectedTimestamp:a,setSelectedTimestamp:i},children:t})},h1=e=>{const t=a=>({...e,columnVisibility:{metadata:!1},annotationColumnVisibility:{},setColumnVisibility:r=>{a({columnVisibility:r})},setAnnotationColumnVisibility:r=>{a({annotationColumnVisibility:r})}});return We()(Je(t))};function fr(){const e=v(a=>a.setPointSizeScale),t=v(a=>a.pointSizeScale);return s(ga,{placement:"bottom left",children:[n(B,{variant:"default",size:"compact",icon:n(I,{svg:n(w.OptionsOutline,{})}),"aria-label":"Display Settings"}),n(pa,{children:n(R,{padding:"size-100",children:n(D,{direction:"column",gap:"size-100",children:n(ma,{label:"Point Scale",minValue:0,maxValue:3,step:.1,value:t,onChange:e})})})})]})}const Sn=m`
  display: flex;
  flex-direction: row;
  gap: var(--px-spacing-sm);
`;function Lr(e){return typeof e=="string"&&e in ue}function yr(e){return s(Re,{defaultValue:e.mode,variant:"inline-button",size:"compact",onChange:t=>{if(Lr(t))e.onChange(t);else throw new Error(`Unknown canvas mode: ${t}`)},children:[n(H,{label:"Move",value:ue.move,children:s(A,{placement:"top",delay:0,offset:10,children:[n(q,{children:s("div",{css:Sn,children:[n(I,{svg:n(w.MoveFilled,{})})," Move"]})}),n(Q,{children:"Move around the canvas using orbital controls"})]})}),n(H,{label:"Select",value:ue.select,children:s(A,{placement:"top",delay:0,offset:10,children:[n(q,{children:s("div",{css:Sn,children:[n(I,{svg:n(w.LassoOutline,{})})," Select"]})}),n(Q,{children:"Select points using the lasso tool"})]})})]})}function vr({radius:e}){const t=v(c=>c.eventIdToDataMap),a=v(c=>c.highlightedClusterId),r=v(c=>c.selectedClusterId),i=v(c=>c.clusters),{theme:l}=U(),o=v(c=>c.clusterColorMode),d=p.useMemo(()=>i.map(c=>{const{eventIds:u}=c,h=u.map(g=>{var L;return{position:(L=t.get(g))==null?void 0:L.position}}).filter(g=>g.position!==null);return{...c,data:h}}).filter(c=>c.data.length>0),[i,t]);return n(Ve,{children:d.map((c,u)=>{const h=Cr({selected:c.id===r,highlighted:c.id===a,clusterColorMode:o});return n(Qt,{data:c.data,opacity:h,wireframe:!0,pointRadius:e,color:br({theme:l,clusterColorMode:o,index:u,clusterCount:d.length})},`${c.id}__opacity_${String(h)}`)})})}function br({theme:e,clusterColorMode:t,index:a,clusterCount:r}){return t===rn.default?e==="dark"?"#999999":"#bbbbbb":Nn(a/r)}function Cr({selected:e,highlighted:t,clusterColorMode:a}){return a===rn.highlight?1:e?.7:t?.5:0}const kr=2;function xr({pointRadius:e}){const t=v(u=>u.hoveredEventId),a=v(u=>u.pointSizeScale),r=v(u=>u.eventIdToDataMap),i=v(u=>u.pointGroupColors),l=v(u=>u.eventIdToGroup);if(t==null||r==null)return null;const o=r.get(t),d=l[t],c=i[d];return o==null?null:n(Ut,{position:o.position,args:[e*kr],scale:[a,a,a],children:n("meshMatcapMaterial",{color:c,opacity:.7,transparent:!0})})}const Mn=1;function wr(){const e=v(i=>i.hoveredEventId),t=v(i=>i.eventIdToDataMap),a=p.useRef(null);Ht((i,l)=>{a.current&&a.current.children.forEach(o=>o.children[0].material.uniforms.dashOffset.value-=l*5)});const r=p.useMemo(()=>{if(e==null)return[];const i=t.get(e);if(i==null)return[];const l=i.retrievals??[];return(l==null?void 0:l.length)===0?[]:l.map(d=>{const c=t.get(d.documentId);return c==null?null:[i.position,c.position]}).filter(d=>d!=null)},[t,e]);return n("group",{ref:a,children:r.map((i,l)=>s("group",{children:[n(un,{start:i[0],end:i[1],color:16777215,opacity:1,transparent:!0,dashed:!0,dashScale:50,gapSize:20,linewidth:Mn}),n(un,{start:i[0],end:i[1],color:16777215,linewidth:Mn/2,transparent:!0,opacity:.8})]},l))})}const Sr=.5,Mr=.5,Tr=100,Tn=1.7;function In(e,t){return typeof t=="function"?t(e):t}function Ir({primaryData:e,referenceData:t,corpusData:a,color:r,radius:i}){const l=v(S=>S.inferencesVisibility),o=v(S=>S.coloringStrategy),{theme:d}=U(),c=v(S=>S.setSelectedEventIds),u=v(S=>S.selectedEventIds),h=v(S=>S.setSelectedClusterId),g=v(S=>S.setHoveredEventId),f=v(S=>S.pointSizeScale),L=p.useMemo(()=>Zt(g,Tr),[g]),y=p.useMemo(()=>o!==M.inferences?"cube":"sphere",[o]),k=p.useMemo(()=>o!==M.inferences?"octahedron":"sphere",[o]),V=p.useMemo(()=>d==="dark"?jt(Sr):qt(Mr),[d]),x=p.useMemo(()=>typeof r=="function"?S=>V(r(S)):V(r),[r,V]),F=p.useCallback(S=>!u.has(S.metaData.id)&&u.size>0?In(S,x):In(S,r),[u,r,x]),Y=l.reference&&t,ge=l.corpus&&a,ee=p.useCallback(S=>{p.startTransition(()=>{c(new Set([S.metaData.id])),h(null)})},[h,c]),ne=p.useCallback(S=>{S==null||S.metaData==null||L(S.metaData.id)},[L]),he=p.useCallback(()=>{L(null)},[L]);return s(Ve,{children:[l.primary?n($e,{data:e,pointProps:{color:F,radius:i,scale:f},onPointClicked:ee,onPointHovered:ne,onPointerLeave:he}):null,Y?n($e,{data:t,pointProps:{color:F,radius:i,size:i?i*Tn:void 0,scale:f},onPointHovered:ne,onPointerLeave:he,pointShape:y,onPointClicked:ee}):null,ge?n($e,{data:a,pointProps:{color:F,radius:i,size:i?i*Tn:void 0,scale:f},onPointHovered:ne,onPointerLeave:he,pointShape:k,onPointClicked:ee}):null]})}const Dr=/\.(mp4|mov|webm|ogg)(\?|$)/i,Er=/\.(mp3|wav)(\?|$)/i;function Fr(e){return Dr.test(e)}function _r(e){return Er.test(e)}var re=(e=>(e.square="square",e.circle="circle",e.diamond="diamond",e))(re||{});const Pr=()=>n("svg",{width:"12px",height:"12px",viewBox:"0 0 12 12",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:n("rect",{width:"12",height:"12",rx:"1",fill:"currentColor"})}),Vr=()=>n("svg",{width:"12px",height:"12px",viewBox:"0 0 12 12",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:n("circle",{cx:"6",cy:"6",r:"6",fill:"currentColor"})}),Nr=()=>n("svg",{width:"12px",height:"12px",viewBox:"0 0 12 12",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:n("path",{d:"M6 0L12 6L6 12L0 6L6 0Z",fill:"currentColor"})});function ft(e){const{shape:t,color:a}=e,r=p.useMemo(()=>{switch(t){case"square":return n(Pr,{});case"circle":return n(Vr,{});case"diamond":return n(Nr,{});default:P()}},[t]);return n("i",{className:"shape-icon",style:{color:a},css:m`
        display: flex;
        flex-direction: row;
        align-items: center;
      `,"aria-hidden":!0,children:r})}function Rr(e){const{rawData:t,linkToData:a,promptAndResponse:r,documentText:i}=e;return i!=null?"document":r!=null?"prompt_response":a!=null?Fr(a)?"video":_r(a)?"audio":"image":t!=null?"raw":"event_metadata"}function Or(e,t){const{rawData:a}=t;switch(e){case"document":return null;case"prompt_response":return null;case"image":return a!=null?"raw":null;case"video":return a!=null?"raw":null;case"audio":return a!=null?"raw":null;case"raw":return"event_metadata";case"event_metadata":return null;default:P()}}function Ar(e){const{onClick:t,onMouseOver:a,onMouseOut:r,color:i,size:l,inferencesName:o,group:d}=e,c=Rr(e),u=l==="large"?Or(c,e):null;return s("div",{"data-testid":"event-item",role:"button","data-size":l,css:m`
        width: 100%;
        height: 100%;
        box-sizing: border-box;
        border-style: solid;
        border-radius: 4px;
        overflow: hidden;

        display: flex;
        flex-direction: column;
        cursor: pointer;
        overflow: hidden;

        border-width: 1px;
        border-color: ${i};
        border-radius: var(--ac-global-rounding-medium);
        transition: border-color 0.2s ease-in-out;
        transition: transform 0.2s ease-in-out;
        &:hover {
          transform: scale(1.04);
        }
        &[data-size="small"] {
          border-width: 2px;
        }
      `,onClick:t,onMouseOver:a,onMouseOut:r,children:[s("div",{className:"event-item__preview-wrap","data-size":l,css:m`
          display: flex;
          flex-direction: row;
          flex: 1 1 auto;
          overflow: hidden;
          & > *:nth-child(1) {
            flex: 1 1 auto;
            overflow: hidden;
          }
          & > *:nth-child(2) {
            flex: none;
            width: 43%;
          }
          &[data-size="large"] {
            & > *:nth-child(1) {
              margin: var(--px-spacing-med);
              border-radius: 8px;
            }
          }
        `,children:[n(Dn,{previewType:c,...e}),u!=null&&n(Dn,{previewType:u,...e})]}),l!=="small"&&n(Hr,{color:i,group:d,inferencesName:o,showInferences:l==="large"})]})}function Dn(e){const{previewType:t}=e;let a=null;switch(t){case"document":{a=n(Br,{...e});break}case"prompt_response":{a=n(Gr,{...e});break}case"image":{a=n(Kr,{...e});break}case"video":{a=n(zr,{...e});break}case"audio":{a=n($r,{...e});break}case"raw":{a=n(Qr,{...e});break}case"event_metadata":{a=n(Ur,{...e});break}default:P()}return a}function Kr(e){return n("img",{src:e.linkToData||"[error] unexpected missing url",css:m`
        min-height: 0;
        // Maintain aspect ratio while having normalized height
        object-fit: contain;
        transition: background-color 0.2s ease-in-out;
        background-color: ${Rn(.85,e.color)};
      `})}function zr(e){return n("video",{src:e.linkToData||"[error] unexpected missing url",css:m`
        min-height: 0;
        // Maintain aspect ratio while having normalized height
        object-fit: contain;
        transition: background-color 0.2s ease-in-out;
        background-color: ${Rn(.85,e.color)};
      `})}function $r(e){return n("audio",{src:e.linkToData||"[error] unexpected missing url",autoPlay:e.autoPlay,controls:!0})}function Gr(e){var t,a;return s("div",{"data-size":e.size,css:m`
        --prompt-response-preview-background-color: var(
          --ac-global-color-grey-200
        );
        background-color: var(--prompt-response-preview-background-color);
        &[data-size="small"] {
          display: flex;
          flex-direction: column;
          padding: var(--px-spacing-sm);
          font-size: var(--px-font-size-sm);
          section {
            flex: 1 1 0;
            overflow: hidden;
            header {
              display: none;
            }
          }
        }
        &[data-size="medium"] {
          display: flex;
          flex-direction: column;
          gap: var(--px-spacing-sm);
          padding: var(--px-spacing-med);
          section {
            flex: 1 1 0;
            overflow: hidden;
          }
        }
        &[data-size="large"] {
          display: flex;
          flex-direction: row;
          section {
            padding: var(--px-spacing-sm);
            flex: 1 1 0;
          }
        }
        & > section {
          position: relative;

          header {
            font-weight: bold;
            margin-bottom: var(--px-spacing-sm);
          }
          &:before {
            content: "";
            width: 100%;
            height: 100%;
            position: absolute;
            left: 0;
            top: 0;
            background: linear-gradient(
              transparent 80%,
              var(--prompt-response-preview-background-color) 100%
            );
          }
        }
      `,children:[s("section",{children:[n("header",{children:"prompt"}),(t=e.promptAndResponse)==null?void 0:t.prompt]}),s("section",{children:[n("header",{children:"response"}),(a=e.promptAndResponse)==null?void 0:a.response]})]})}function Br(e){return n("p",{"data-size":e.size,css:m`
        flex: 1 1 auto;
        padding: var(--px-spacing-med);
        margin-block-start: 0;
        margin-block-end: 0;
        position: relative;
        --text-preview-background-color: var(--ac-global-color-grey-100);
        background-color: var(--text-preview-background-color);

        &[data-size="small"] {
          padding: var(--px-spacing-sm);
          box-sizing: border-box;
        }
        &:before {
          content: "";
          width: 100%;
          height: 100%;
          position: absolute;
          left: 0;
          top: 0;
          background: linear-gradient(
            transparent 90%,
            var(--text-preview-background-color) 98%,
            var(--text-preview-background-color) 100%
          );
        }
      `,children:e.documentText})}function Qr(e){return n("p",{"data-size":e.size,css:m`
        flex: 1 1 auto;
        padding: var(--px-spacing-med);
        margin-block-start: 0;
        margin-block-end: 0;
        position: relative;
        --text-preview-background-color: var(--ac-background-color-light);
        background-color: var(--text-preview-background-color);

        &[data-size="small"] {
          padding: var(--px-spacing-sm);
          font-size: var(--ac-global-color-gray-600);
          box-sizing: border-box;
        }
        &:before {
          content: "";
          width: 100%;
          height: 100%;
          position: absolute;
          left: 0;
          top: 0;
          background: linear-gradient(
            transparent 90%,
            var(--text-preview-background-color) 98%,
            var(--text-preview-background-color) 100%
          );
        }
      `,children:e.rawData})}function Ur(e){return s("dl",{css:m`
        margin: 0;
        padding: var(--px-spacing-lg);
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: var(--px-spacing-med);

        dt {
          font-weight: bold;
        }
        dd {
          margin-inline-start: var(--px-spacing-med);
        }
      `,children:[s("div",{children:[n("dt",{children:"prediction label"}),n("dd",{children:e.predictionLabel||"--"})]}),s("div",{children:[n("dt",{children:"actual label"}),n("dd",{children:e.actualLabel||"--"})]})]})}function Hr({color:e,group:t,showInferences:a,inferencesName:r}){return s("footer",{css:m`
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        padding: var(--px-spacing-sm) var(--px-spacing-med) var(--px-spacing-sm)
          7px;
        border-top: 1px solid var(--ac-global-border-color-dark);
      `,children:[s("div",{css:m`
          display: flex;
          flex-direction: row;
          align-items: center;
          gap: var(--px-spacing-sm);
        `,children:[n(ft,{shape:re.circle,color:e}),t]}),a?n("div",{title:"the inferences the point belongs to",children:r}):null]})}const fe=200,Ie=10,Zr=new Sa,jr=()=>{const{getInferencesNameByRole:e}=Oe(),t=v(f=>f.hoveredEventId),a=v(f=>f.eventIdToDataMap),r=v(f=>f.pointData),i=v(f=>f.pointGroupColors),l=v(f=>f.eventIdToGroup);if(t==null||r==null||r==null)return null;const o=a.get(t),d=r[t];if(o==null||d==null)return null;const c=l[t],u=i[l[t]],h=Jn(t),g=e(h);return n(Wt,{position:o.position,pointerEvents:"none",zIndexRange:[0,1],calculatePosition:(f,L,y)=>{const k=Zr.setFromMatrixPosition(f.matrixWorld);k.project(L);const V=y.width/2,x=y.height/2;return[Math.min(y.width-fe-Ie,Math.max(0,k.x*V+V+Ie)),Math.min(y.height-fe-Ie,Math.max(0,-(k.y*x)+x+Ie))]},children:n("div",{css:m`
          --grid-item-min-width: ${fe}px;
          width: ${fe}px;
          height: ${fe}px;
          background-color: var(--ac-global-background-color-dark);
          border-radius: var(--ac-global-rounding-medium);
        `,children:n(Ar,{rawData:o.embeddingMetadata.rawData,linkToData:o.embeddingMetadata.linkToData,predictionLabel:o.eventMetadata.predictionLabel,actualLabel:o.eventMetadata.actualLabel,promptAndResponse:d.promptAndResponse,documentText:d.documentText,inferencesName:g,group:c,color:u,size:"medium",autoPlay:!0})})})},qr=300,Wr=3,Jr=.2,Xr=function(){const{selectedTimestamp:t}=hr(),a=v(c=>c.points),r=v(c=>c.hdbscanParameters),i=v(c=>c.umapParameters),[l,o,d]=p.useMemo(()=>{const{primaryEventIds:c,referenceEventIds:u,corpusEventIds:h}=an(a.map(g=>g.eventId));return[c.length,u.length,h.length]},[a]);return t?s("section",{css:m`
        width: 300px;
        padding: var(--px-spacing-med);
      `,children:[s("dl",{css:Qe,children:[s("div",{children:[n("dt",{children:"Timestamp"}),n("dd",{children:je(t)})]}),s("div",{children:[n("dt",{children:"primary points"}),n("dd",{children:l})]}),o>0?s("div",{children:[n("dt",{children:"reference points"}),n("dd",{children:o})]}):null,d>0?s("div",{children:[n("dt",{children:"corpus points"}),n("dd",{children:d})]}):null]}),n("br",{}),n(O,{level:4,weight:"heavy",children:"Clustering Parameters"}),s("dl",{css:Qe,children:[s("div",{children:[n("dt",{children:"min cluster size"}),n("dd",{children:r.minClusterSize})]}),s("div",{children:[n("dt",{children:"cluster min samples"}),n("dd",{children:r.clusterMinSamples})]}),s("div",{children:[n("dt",{children:"cluster selection epsilon"}),n("dd",{children:r.clusterSelectionEpsilon})]})]}),n("br",{}),n(O,{level:4,weight:"heavy",children:"UMAP Parameters"}),s("dl",{css:Qe,children:[s("div",{children:[n("dt",{children:"min distance"}),n("dd",{children:i.minDist})]}),s("div",{children:[n("dt",{children:"n neighbors"}),n("dd",{children:i.nNeighbors})]}),s("div",{children:[n("dt",{children:"n samples per inferences"}),n("dd",{children:i.nSamples})]})]})]}):null},Qe=m`
  margin: 0;
  padding: 0;
  div {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: var(--px-spacing-sm);
  }
`;function Yr(){const e=v(a=>a.canvasMode),t=v(a=>a.setCanvasMode);return s("div",{css:m`
        position: absolute;
        left: var(--px-spacing-med);
        top: var(--px-spacing-med);
        z-index: 1;
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: var(--px-spacing-med);
      `,children:[n(yr,{mode:e,onChange:t}),n(fr,{}),n(ei,{})]})}function ei(){return s(A,{placement:"bottom left",delay:0,children:[n(B,{variant:"default",size:"compact",icon:n(I,{svg:n(ha,{})}),"aria-label":"Information bout the point-cloud display"}),n(fa,{title:"Point Cloud Summary",children:n(Xr,{})})]})}function ni({children:e}){const{theme:t}=U();return n("div",{css:m`
        flex: 1 1 auto;
        height: 100%;
        position: relative;
        &[data-theme="dark"] {
          background: linear-gradient(
            rgb(21, 25, 31) 11.4%,
            rgb(11, 12, 14) 70.2%
          );
        }
        &[data-theme="light"] {
          background: linear-gradient(#f2f6fd 0%, #dbe6fc 74%);
        }
      `,"data-theme":t,children:e})}function f1(){return s(ni,{children:[n(Yr,{},"canvas-tools"),n(ti,{},"projection")]})}const ti=W.memo(function(){const t=v(b=>b.points),a=v(b=>b.canvasMode),r=v(b=>b.setSelectedEventIds),i=v(b=>b.setSelectedClusterId),l=v(b=>b.pointGroupColors),o=v(b=>b.pointGroupVisibility),{theme:d}=U(),c=v(b=>b.inferencesVisibility),[u,h]=p.useState(!0),g=p.useMemo(()=>Jt(t.map(b=>b.position)),[t]),f=(g.maxX-g.minX+(g.maxY-g.minY))/2/qr,L=f*Wr,y=a===ue.move,k=v(b=>b.eventIdToGroup),V=p.useCallback(b=>{const K=k[b.metaData.id]||"unknown";return l[K]||le},[l,k]),x=p.useMemo(()=>t.filter(b=>b.eventId.includes("PRIMARY")),[t]),F=p.useMemo(()=>t.filter(b=>b.eventId.includes("REFERENCE")),[t]),Y=p.useMemo(()=>t.filter(b=>b.eventId.includes("CORPUS")),[t]),ge=p.useMemo(()=>x.filter(b=>{const K=k[b.eventId];return o[K]}),[x,k,o]),ee=p.useMemo(()=>!F||F.length===0?null:F.filter(b=>{const K=k[b.eventId];return o[K]}),[F,k,o]),ne=p.useMemo(()=>Y.filter(b=>{const K=k[b.eventId];return o[K]}),[Y,k,o]),he=p.useMemo(()=>{const b=c.primary?ge:[],K=c.reference?ee:[],Et=c.corpus?ne:[];return[...b,...K||[],...Et||[]]},[ge,ee,ne,c]),S=Xt(ln,tn,ra,on);return n(aa,{camera:{position:[3,3,3]},children:s(S,{children:[n(Yt,{autoRotate:u,autoRotateSpeed:2,enableRotate:y,enablePan:y,onEnd:()=>{h(!1)}}),s(ea,{bounds:g,boundsZoomPaddingFactor:Jr,children:[n(na,{points:he,onChange:b=>{r(new Set(b.map(K=>K.metaData.id))),i(null)},enabled:a===ue.select}),n(ta,{size:(g.maxX-g.minX)/4,color:d=="dark"?"#fff":"#505050"}),n(Ir,{primaryData:ge,referenceData:ee,corpusData:ne,color:V,radius:f}),n(vr,{radius:L}),n(jr,{}),n(xr,{pointRadius:f}),n(wr,{})]})]})})}),Lt=function(){var e=[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:null,args:null,concreteType:"DimensionConnection",kind:"LinkedField",name:"dimensions",plural:!1,selections:[{alias:null,args:null,concreteType:"DimensionEdge",kind:"LinkedField",name:"edges",plural:!0,selections:[{alias:null,args:null,concreteType:"Dimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"type",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"dataType",storageKey:null}],storageKey:null}],storageKey:null}],storageKey:null}],storageKey:null}];return{fragment:{argumentDefinitions:[],kind:"Fragment",metadata:null,name:"DimensionPickerQuery",selections:e,type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[],kind:"Operation",name:"DimensionPickerQuery",selections:e},params:{cacheID:"56e356d226d322dabfd9db8010884e4f",id:null,metadata:{},name:"DimensionPickerQuery",operationKind:"query",text:`query DimensionPickerQuery {
  model {
    dimensions {
      edges {
        node {
          id
          name
          type
          dataType
        }
      }
    }
  }
}
`}}}();Lt.hash="747256fac1de97803ae6f96e3cb58d98";function ai(e){const{type:t}=e;let a="gray",r="";switch(t){case"feature":a="blue",r="FEA";break;case"tag":a="purple",r="TAG";break;case"prediction":a="white",r="PRE";break;case"actual":a="orange",r="ACT";break;default:P()}return n(Xe,{color:a,"aria-label":t,title:"type",children:r})}const ri=s(X,{children:[n(O,{weight:"heavy",level:4,children:"Model Dimension"}),n(J,{children:n(C,{children:"A dimension is a feature, tag, prediction, or actual value that is associated with a model inference. Features represent inputs, tags represent metadata, predictions represent outputs, and actuals represent ground truth."})})]});function ii(e){const{selectedDimension:t,dimensions:a,onChange:r,isLoading:i,...l}=e;return n(xe,{...l,defaultSelectedKey:t?t.name:void 0,"aria-label":"Select a dimension",onSelectionChange:o=>{const d=a.find(c=>c.name===o);d&&p.startTransition(()=>r(d))},label:"Dimension",labelExtra:ri,isDisabled:i,placeholder:i?"Loading...":"Select a dimension...",children:a.map(o=>n(_,{textValue:o.name,children:s("div",{css:m`
              .ac-label {
                margin-right: var(--px-spacing-med);
              }
            `,children:[n(ai,{type:o.type}),o.name]})},o.name))})}function li(e){const[t,a]=p.useState([]),[r,i]=p.useState(!0),{selectedDimension:l,onChange:o,...d}=e;return p.useEffect(()=>{Z.fetchQuery(Se,Lt,{},{fetchPolicy:"store-or-network"}).toPromise().then(c=>{const u=(c==null?void 0:c.model.dimensions.edges.map(h=>h.node))??[];a(u),i(!1)})},[]),n(ii,{...d,onChange:o,dimensions:t,label:"Dimension",selectedDimension:l,isLoading:r})}function oi(e){return typeof e=="string"&&e in M}const si=Object.values(M),ci=s(X,{children:[n(O,{weight:"heavy",level:4,children:"Coloring Strategy"}),n(J,{children:n(C,{children:"The way in which inference point is colored. Each point in the point-cloud represents a model inference. These inferences can be colored by a particular attribute (such as inferences and dimension) or by a performance value such as correctness (predicted value equals the actual value)"})})]});function di(e){const{strategy:t,onChange:a}=e;return n(xe,{defaultSelectedKey:t,"aria-label":"Coloring strategy",onSelectionChange:r=>{oi(r)&&a(r)},label:"Color By",labelExtra:ci,children:si.map(r=>n(_,{children:r},r))})}const ui=m`
  display: flex;
  flex-direction: row;
  gap: var(--px-flex-gap-sm);
  align-items: center;
`;function Ee(e){const{name:t,checked:a,onChange:r,color:i,iconShape:l=re.circle}=e;return s("label",{css:ui,children:[n("input",{type:"checkbox",checked:a,name:t,onChange:r}),n(ft,{shape:l,color:i}),t]},t)}function mi({hasReference:e,hasCorpus:t}){const a=v(f=>f.inferencesVisibility),r=v(f=>f.setInferencesVisibility),i=v(f=>f.coloringStrategy),l=p.useCallback(f=>{const{name:L,checked:y}=f.target;r({...a,[L]:y})},[a,r]),o=wa(),d=p.useMemo(()=>{switch(i){case M.inferences:return o[0];case M.correctness:case M.dimension:return j;default:P()}},[i,o]),c=p.useMemo(()=>{switch(i){case M.inferences:return o[1];case M.correctness:case M.dimension:return j;default:P()}},[i,o]),u=j,h=i===M.inferences?re.circle:re.square,g=i===M.inferences?re.circle:re.diamond;return s("form",{css:m`
        display: flex;
        flex-direction: column;
        padding: var(--px-spacing-med);
      `,children:[n(Ee,{checked:a.primary,name:"primary",color:d,onChange:l}),e?n(Ee,{checked:a.reference,name:"reference",onChange:l,color:c,iconShape:h}):null,t?n(Ee,{checked:a.corpus,name:"corpus",onChange:l,color:u,iconShape:g}):null]})}function pi(){const e=v(l=>l.pointGroupVisibility),t=v(l=>l.setPointGroupVisibility),a=v(l=>l.pointGroupColors),r=p.useMemo(()=>Object.keys(e),[e]),i=p.useCallback(l=>{const{name:o,checked:d}=l.target;t({...e,[o]:d})},[e,t]);return s("form",{css:m`
        display: flex;
        flex-direction: column;
      `,children:[n(gi,{}),n("div",{css:m`
          padding: var(--px-spacing-med);
        `,children:r.map(l=>{const o=e[l],d=a[l];return n(Ee,{name:l,checked:o,color:d,onChange:i},l)})})]})}function gi(){const e=v(l=>l.pointGroupVisibility),t=v(l=>l.setPointGroupVisibility),a=v(l=>l.coloringStrategy),r=p.useMemo(()=>Object.values(e).every(l=>!l),[e]),i=p.useCallback(l=>{const{checked:o}=l.target,d=Object.keys(e).reduce((c,u)=>(c[u]=o,c),{});t(d)},[e,t]);return s("label",{css:()=>m`
        display: flex;
        flex-direction: row;
        gap: var(--px-flex-gap-sm);
        padding: var(--px-spacing-sm) var(--px-spacing-med);
        background-color: var(--ac-global-background-color-light);
      `,children:[n("input",{type:"checkbox",checked:!r,onChange:i}),`${a}`]})}function L1(){const{referenceInferences:e,corpusInferences:t}=Oe(),a=v(g=>g.coloringStrategy),r=v(g=>g.setColoringStrategy),i=v(g=>g.dimension),l=v(g=>g.dimensionMetadata),o=v(g=>g.setDimension),d=e!=null||t!=null,c=a===M.dimension&&i==null,u=a===M.dimension&&i!=null&&l==null,h=a!==M.inferences&&!c&&!u;return s("section",{css:m`
        & > .ac-form {
          padding: var(--px-spacing-med) var(--px-spacing-med) 0
            var(--px-spacing-med);
        }
        & > .ac-alert {
          margin: var(--px-spacing-med);
        }
      `,children:[n(we,{children:s(Ve,{children:[n(di,{strategy:a,onChange:r}),a===M.dimension?n(li,{selectedDimension:null,onChange:g=>{o(g)}}):null]})}),d?n(mi,{hasReference:e!=null,hasCorpus:t!=null}):null,h?n(pi,{}):null,c?n(La,{variant:"info",showIcon:!1,children:"Please select a dimension to color the point cloud by"}):null,u?n("div",{css:m`
            padding: var(--px-spacing-med);
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
          `,children:n(mr,{message:"Calculating point colors"})}):null]})}function hi(e){return typeof e=="string"&&e in de}function y1(e){return s(Re,{defaultValue:e.mode,variant:"inline-button",onChange:t=>{if(hi(t))e.onChange(t);else throw new Error(`Unknown view mode: ${t}`)},children:[n(H,{label:"List",value:de.list,children:n(I,{svg:n(w.ListOutline,{})})}),n(H,{label:"Grid",value:de.gallery,children:n(I,{svg:n(w.Grid,{})})})]})}function v1(e){const{driftRatio:t,primaryToCorpusRatio:a,clusterId:r,isSelected:i,onClick:l,onMouseEnter:o,onMouseLeave:d,metricName:c,primaryMetricValue:u,referenceMetricValue:h,hideReference:g}=e,{percentage:f,comparisonInferencesRole:L}=p.useMemo(()=>typeof a=="number"?{percentage:(a+1)/2*100,comparisonInferencesRole:G.corpus}:typeof t=="number"?{percentage:(t+1)/2*100,comparisonInferencesRole:G.reference}:{percentage:100,comparisonInferencesRole:null},[t,a]);return s("div",{css:m`
        border: 1px solid var(--ac-global-border-color-light);
        border-radius: var(--ac-global-rounding-medium);
        overflow: hidden;
        transition: background-color 0.2s ease-in-out;
        cursor: pointer;
        &:hover {
          background-color: var(--ac-global-color-primary-700);
          border-color: var(--ac-global-color-primary);
        }
        &.is-selected {
          border-color: var(--ac-global-color-primary);
          background-color: var(--ac-global-color-primary-700);
        }
      `,className:i?"is-selected":"",role:"button",onClick:l,onMouseEnter:o,onMouseLeave:d,children:[s("div",{css:m`
          padding: var(--ac-global-dimension-static-size-100);
          display: flex;
          flex-direction: row;
          justify-content: space-between;
          align-items: center;
        `,children:[n(D,{"data-testid":"cluster-description",direction:"column",gap:"size-50",alignItems:"start",children:s(D,{direction:"column",alignItems:"start",children:[n(O,{level:3,children:`Cluster ${r}`}),n(C,{color:"text-700",textSize:"small",children:`${e.numPoints} points`})]})}),s("div",{"data-testid":"cluster-metric",css:m`
            display: flex;
            flex-direction: column;
            align-items: end;
          `,children:[n(C,{color:"text-700",textSize:"small",children:c}),n(C,{color:"text-900",textSize:"medium",children:kn(u)}),g?null:n(C,{color:"designationPurple",textSize:"small",children:kn(h)})]})]}),n(fi,{primaryPercentage:f,comparisonInferencesRole:L})]})}function fi({primaryPercentage:e,comparisonInferencesRole:t}){return s("div",{"data-testid":"inferences-distribution",css:m`
        display: flex;
        flex-direction: row;
      `,children:[n("div",{"data-testid":"primary-distribution",css:m`
          background-image: linear-gradient(
            to right,
            var(--px-primary-color--transparent) 0%,
            var(--px-primary-color)
          );
          height: var(--px-gradient-bar-height);
          width: ${e}%;
        `}),n("div",{"data-testid":"reference-distribution","data-reference-inferences-role":`${t??"none"}`,css:m`
          &[data-reference-inferences-role="reference"] {
            background-image: linear-gradient(
              to right,
              var(--px-reference-color) 0%,
              var(--px-reference-color--transparent)
            );
          }
          &[data-reference-inferences-role="corpus"] {
            background-image: linear-gradient(
              to right,
              var(--px-corpus-color) 0%,
              var(--px-corpus-color--transparent)
            );
          }

          height: var(--px-gradient-bar-height);
          width: ${100-e}%;
        `})]})}const Li=s(X,{children:[n(O,{weight:"heavy",level:4,children:"UMAP N Neighbors"}),n(J,{children:n(C,{children:"This parameter controls how UMAP balances local versus global structure in the data. It does this by constraining the size of the local neighborhood UMAP will look at when attempting to learn the manifold structure of the data. This means that low values of n_neighbors will force UMAP to concentrate on very local structure (potentially to the detriment of the big picture), while large values will push UMAP to look at larger neighborhoods of each point when estimating the manifold structure of the data, losing fine detail structure for the sake of getting the broader of the data."})}),n("footer",{children:n(pe,{href:"https://umap-learn.readthedocs.io/en/latest/parameters.html#n-neighbors",children:"View UMAP documentation"})})]}),yi=s(X,{children:[n(O,{weight:"heavy",level:4,children:"UMAP Minimum Distance"}),n(J,{children:n(C,{children:"The min_dist parameter controls how tightly UMAP is allowed to pack points together. It, quite literally, provides the minimum distance apart that points are allowed to be in the low dimensional representation. This means that low values of min_dist will result in clumpier embeddings. This can be useful if you are interested in clustering, or in finer topological structure. Larger values of min_dist will prevent UMAP from packing points together and will focus on the preservation of the broad topological structure instead."})}),n("footer",{children:n(pe,{href:"https://umap-learn.readthedocs.io/en/latest/parameters.html#min-dist",children:"View UMAP documentation"})})]}),vi=s(X,{children:[n(O,{weight:"heavy",level:4,children:"Number of Samples"}),s(J,{children:[n(C,{elementType:"p",children:"Determines the number of samples from each inferences to use when projecting the point cloud using UMAP. This number is per-inferences so a value of 500 means that the point cloud will contain up to 1000 points."}),n("br",{}),n(C,{elementType:"p",children:"For best results keep this value low until you have identified a sample that you would like to analyze in more detail."})]})]});function b1(){const e=v(c=>c.umapParameters),t=v(c=>c.setUMAPParameters),{handleSubmit:a,control:r,setError:i,formState:{isDirty:l,isValid:o}}=Ne({reValidateMode:"onChange",defaultValues:e}),d=p.useCallback(c=>{const u=parseFloat(c.minDist);if(u<gn||u>hn){i("minDist",{message:`must be between ${gn} and ${hn}`});return}t({minDist:u,nNeighbors:parseInt(c.nNeighbors,10),nSamples:parseInt(c.nSamples,10)})},[t,i]);return n("section",{css:m`
        & > .ac-form {
          padding: var(--px-spacing-med) var(--px-spacing-med) 0
            var(--px-spacing-med);
        }
      `,children:s(we,{onSubmit:a(d),children:[n(N,{name:"minDist",control:r,rules:{required:"field is required"},render:({field:{onChange:c,onBlur:u,value:h},fieldState:{invalid:g,error:f}})=>n($,{label:"min distance",labelExtra:yi,type:"number",description:"how tightly to pack points",errorMessage:f==null?void 0:f.message,validationState:g?"invalid":"valid",onChange:L=>c(parseFloat(L)),onBlur:u,value:h.toString()})}),n(N,{name:"nNeighbors",control:r,rules:{required:"n neighbors is required",min:{value:mn,message:`greater than or equal to ${mn}`},max:{value:pn,message:`less than or equal to ${pn}`}},render:({field:c,fieldState:{invalid:u,error:h}})=>n($,{label:"n neighbors",labelExtra:Li,type:"number",step:"0.01",description:"balances local versus global structure",errorMessage:h==null?void 0:h.message,validationState:u?"invalid":"valid",...c,value:c.value})}),n(N,{name:"nSamples",control:r,rules:{required:"n samples is required",max:{value:Ln,message:`must be below ${Ln}`},min:{value:fn,message:`must be above ${fn}`}},render:({field:{onChange:c,onBlur:u,value:h},fieldState:{invalid:g,error:f}})=>n($,{label:"n samples",labelExtra:vi,defaultValue:"500",type:"number",description:"number of points to use per inferences",errorMessage:f==null?void 0:f.message,validationState:g?"invalid":"valid",onChange:L=>c(parseInt(L,10)),onBlur:u,value:h.toString()})}),n("div",{css:m`
            display: flex;
            flex-direction: row;
            justify-content: flex-end;
            margin-top: var(--px-spacing-med);
          `,children:n(B,{variant:l?"primary":"default",type:"submit",isDisabled:!o,css:m`
              width: 100%;
            `,children:"Apply UMAP Parameters"})})]})})}const Ue=2147483647,bi=s(X,{children:[n(O,{weight:"heavy",level:4,children:"Minimum Cluster Size"}),n(J,{children:n(C,{elementType:"p",children:"The primary parameter to effect the resulting clustering is min_cluster_size. Ideally this is a relatively intuitive parameter to select – set it to the smallest size grouping that you wish to consider a cluster."})}),n("footer",{children:n(pe,{href:"https://hdbscan.readthedocs.io/en/latest/parameter_selection.html#selecting-min-cluster-size",children:"View HDBSCAN documentation"})})]}),Ci=s(X,{children:[n(O,{weight:"heavy",level:4,children:"Minimum Samples"}),n(J,{children:n(C,{elementType:"p",children:"The simplest intuition for what min_samples does is provide a measure of how conservative you want you clustering to be. The larger the value of min_samples you provide, the more conservative the clustering – more points will be declared as noise, and clusters will be restricted to progressively more dense areas."})}),n("footer",{children:n(pe,{href:"https://hdbscan.readthedocs.io/en/latest/parameter_selection.html#selecting-min-samples",children:"View HDBSCAN documentation"})})]}),ki=s(X,{children:[n(O,{weight:"heavy",level:4,children:"Cluster Selection Epsilon"}),n(J,{children:n(C,{elementType:"p",children:"In some cases, we want to choose a small min_cluster_size because even groups of few points might be of interest to us. However, if our data set also contains partitions with high concentrations of objects, this parameter setting can result in a large number of micro-clusters. Selecting a value for cluster_selection_epsilon helps us to merge clusters in these regions. Or in other words, it ensures that clusters below the given threshold are not split up any further."})}),n("footer",{children:n(pe,{href:"https://hdbscan.readthedocs.io/en/latest/parameter_selection.html#selecting-cluster-selection-epsilon",children:"View HDBSCAN documentation"})})]});function C1(){const e=v(u=>u.hdbscanParameters),t=v(u=>u.setHDBSCANParameters),a=v(u=>u.clustersLoading),{control:r,handleSubmit:i,formState:{isDirty:l,isValid:o},reset:d}=Ne({defaultValues:e}),c=p.useCallback(u=>{const h={minClusterSize:parseInt(u.minClusterSize,10),clusterMinSamples:parseInt(u.clusterMinSamples,10),clusterSelectionEpsilon:parseFloat(u.clusterSelectionEpsilon)};t(h),d(h)},[t,d]);return n("section",{css:m`
        & > .ac-form {
          padding: var(--px-spacing-med) var(--px-spacing-med) 0
            var(--px-spacing-med);
        }
      `,children:s(we,{onSubmit:i(c),children:[n(N,{name:"minClusterSize",control:r,rules:{required:"field is required",min:{value:Va,message:"must be greater than 1"},max:{value:Ue,message:"must be less than 2,147,483,647"}},render:({field:{onChange:u,onBlur:h,value:g},fieldState:{invalid:f,error:L}})=>n($,{label:"min cluster size",labelExtra:bi,type:"number",description:"the smallest size for a cluster",errorMessage:L==null?void 0:L.message,validationState:f?"invalid":"valid",onChange:y=>u(parseInt(y,10)),onBlur:h,value:g.toString()})}),n(N,{name:"clusterMinSamples",control:r,rules:{required:"field is required",min:{value:yn,message:`must be greater than ${yn}`},max:{value:Ue,message:"must be less than 2,147,483,647"}},render:({field:{onBlur:u,onChange:h,value:g},fieldState:{invalid:f,error:L}})=>n($,{label:"cluster minimum samples",labelExtra:Ci,type:"number",description:"determines if a point is a core point",errorMessage:L==null?void 0:L.message,validationState:f?"invalid":"valid",onChange:y=>h(parseInt(y,10)),onBlur:u,value:g.toString()})}),n(N,{name:"clusterSelectionEpsilon",control:r,rules:{required:"field is required",min:{value:0,message:"must be a non-negative number"},max:{value:Ue,message:"must be less than 2,147,483,647"}},render:({field:{onBlur:u,onChange:h,value:g},fieldState:{invalid:f,error:L}})=>n($,{label:"cluster selection epsilon",labelExtra:ki,type:"number",description:"A distance threshold",errorMessage:L==null?void 0:L.message,validationState:f?"invalid":"valid",onChange:y=>h(parseInt(y,10)),onBlur:u,value:g.toString()})}),n("div",{css:m`
            display: flex;
            flex-direction: row;
            justify-content: flex-end;
            margin-top: var(--px-spacing-med);
          `,children:n(B,{variant:l?"primary":"default",type:"submit",isDisabled:!o,loading:a,css:m`
              width: 100%;
            `,children:a?"Applying parameters":"Apply Clustering Config"})})]})})}const k1=m`
  transition: 250ms linear all;
  background-color: var(--ac-global-color-grey-200);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.8px;
  --px-resize-handle-size: 8px;
  --px-resize-icon-width: 24px;
  --px-resize-icon-height: 2px;
  outline: none;
  &[data-panel-group-direction="vertical"] {
    height: var(--px-resize-handle-size);
    flex-direction: column;
    &:before,
    &:after {
      width: var(--px-resize-icon-width);
      height: var(--px-resize-icon-height);
    }
  }
  &[data-panel-group-direction="horizontal"] {
    width: var(--px-resize-handle-size);
    flex-direction: row;
    &:before,
    &:after {
      width: var(--px-resize-icon-height);
      height: var(--px-resize-icon-width);
    }
  }

  &:hover {
    background-color: var(--ac-global-color-grey-300);
    border-radius: 4px;
    &:before,
    &:after {
      background-color: var(--ac-global-color-primary);
    }
  }

  &:before,
  &:after {
    content: "";
    color: var(--color-solid-resize-bar);
    flex: 0 0 1rem;
    border-radius: 6px;
    background-color: var(--ac-global-color-grey-300);
    flex: none;
  }
`,x1=e=>m`
  transition: 250ms linear all;
  background-color: var(--ac-global-color-grey-200);
  --px-resize-handle-size: 4px;
  outline: none;
  &[data-panel-group-direction="vertical"] {
    height: var(--px-resize-handle-size);
  }
  &[data-panel-group-direction="horizontal"] {
    width: var(--px-resize-handle-size);
  }

  &:hover {
    background-color: ${e.colors.arizeLightBlue};
  }
`;function w1(e){return n("div",{css:m`
        background-color: var(--ac-global-color-grey-200);
        border: 1px solid var(--ac-global-color-grey-300);
        padding: var(--px-spacing-med);
        border-radius: var(--ac-global-rounding-medium);
        display: flex;
        flex-direction: column;
        gap: var(--px-spacing-sm);
        min-width: 200px;
      `,children:e.children})}function S1(e){return s("div",{css:m`
        display: flex;
        flex-direction: row;
        justify-content: space-between;
      `,children:[s("div",{css:m`
          display: flex;
          flex-direction: row;
          gap: var(--px-spacing-med);
          align-items: center;
        `,children:[n(wi,{color:e.color,shape:e.shape??"line"}),n(C,{children:e.name})]}),n(C,{children:e.value})]})}function M1(){return n("div",{css:m`
        height: 1px;
        background-color: var(--ac-global-color-grey-300);
        width: 100%;
      `})}const xi=e=>{if(e==="line")return m`
      width: 8px;
      height: 2px;
    `;if(e==="circle")return m`
      width: 8px;
      height: 8px;
      border-radius: 50%;
    `;if(e==="square")return m`
      width: 8px;
      height: 8px;
    `};function wi({color:e,shape:t="line"}){return n("div",{css:m(xi(t),m`
          background-color: ${e};
          flex: none;
        `)})}const T1={dataKey:"timestamp",stroke:"var(--ac-global-colo-grey-400)",style:{fill:"var(--ac-global-text-color-700)"},scale:"time",type:"number",domain:["auto","auto"],padding:"gap"},I1={stroke:"var(--ac-global-color-grey-900)",label:{value:"▼",position:"top",style:{fill:"#fabe32",fontSize:zn.typography.sizes.small.fontSize}}},D1={cursor:{fill:"var(--ac-global-color-grey-300)"}},Ce=60,ke=Ce*24,He=2*ke;function E1(e){const{start:t,end:a}=e,r=Math.floor((a.valueOf()-t.valueOf())/1e3/60/60);return r<=1?{evaluationWindowMinutes:1,samplingIntervalMinutes:1}:r<=24?{evaluationWindowMinutes:Ce,samplingIntervalMinutes:Ce}:{evaluationWindowMinutes:ke,samplingIntervalMinutes:ke}}function F1(e){const{start:t,end:a}=e,r=Math.floor((a.valueOf()-t.valueOf())/1e3/60/60);return r<=1?{evaluationWindowMinutes:He,samplingIntervalMinutes:1}:r<=24?{evaluationWindowMinutes:He,samplingIntervalMinutes:Ce}:{evaluationWindowMinutes:He,samplingIntervalMinutes:ke}}function Si(e){let t;return e<Ce?t="%H:%M %p":e<ke?t="%x %H:%M %p":t="%-m/%-d",t}function _1(e){const t=e.samplingIntervalMinutes;return p.useMemo(()=>Pe(Si(t)),[t])}const Mi=Object.freeze({blue100:"#A4C7E0",blue200:"#7EB0D2",blue300:"#5899C5",blue400:"#3C80AE",blue500:"#2F6488",orange100:"#FECC95",orange200:"#FDB462",orange300:"#FC9C31",orange400:"#F78403",orange500:"#C46903",purple100:"#BEBADA",purple200:"#9E98C8",purple300:"#7F77B6",purple400:"#6157A3",purple500:"#4D4581",pink100:"#FCCDE5",pink200:"#F99FCD",pink300:"#F66FB4",pink400:"#F33F9B",pink500:"#F10E82",gray100:"#f0f0f0",gray200:"#d9d9d9",gray300:"#bdbdbd",gray400:"#969696",gray500:"#737373",gray600:"#525252",gray700:"#252525",default:"#ffffff",primary:"#9efcfd",reference:"#baa1f9"}),Ti=Object.freeze({default:"#000000",blue100:"#2F6488",blue200:"#3C80AE",blue300:"#5899C5",blue400:"#7EB0D2",blue500:"#A4C7E0",orange100:"#C46903",orange200:"#F78403",orange300:"#FC9C31",orange400:"#FDB462",orange500:"#FECC95",purple100:"#4D4581",purple200:"#6157A3",purple300:"#7F77B6",purple400:"#9E98C8",purple500:"#BEBADA",pink100:"#F10E82",pink200:"#F33F9B",pink300:"#F66FB4",pink400:"#F99FCD",pink500:"#FCCDE5",gray100:"#252525",gray200:"#525252",gray300:"#737373",gray400:"#969696",gray500:"#bdbdbd",gray600:"#d9d9d9",gray700:"#f0f0f0",primary:"#00add0",reference:"#4500d9"}),P1=()=>{const{theme:e}=U();return p.useMemo(()=>e==="dark"?Mi:Ti,[e])};function V1(e){switch(e.__typename){case"NominalBin":return e.name;case"IntervalBin":return`${qe(e.range.start)} - ${qe(e.range.end)}`;case"MissingValueBin":return"(empty)";case"%other":throw new Error("Unexpected bin type %other");default:P()}}function Ii(e){return typeof e=="string"&&e in ce}function N1(e){return s(Re,{defaultValue:e.size,variant:"inline-button",onChange:t=>{if(Ii(t))e.onChange(t);else throw new Error(`Unknown grid size: ${t}`)},children:[n(H,{label:"Small",value:ce.small,children:"S"}),n(H,{label:"Medium",value:ce.medium,children:"M"}),n(H,{label:"Large",value:ce.large,children:"L"})]})}function R1(e){const{message:t,...a}=e;return n("div",{css:m`
        width: 100%;
        display: flex;
        justify-content: center;
      `,children:s("div",{css:r=>m`
          margin: ${r.spacing.margin24}px;
          display: flex;
          flex-direction: column;
          align-items: center;
        `,children:[n($n,{...a}),t&&n(C,{children:t})]})})}function Di({color:e}){return n("span",{css:m`
        background-color: ${e};
        display: inline-block;
        width: 0.6rem;
        height: 0.6rem;
        border-radius: 2px;
      `})}const Ei=e=>p.useMemo(()=>{const a=e.charCodeAt(0);return Nn(a%26/26)},[e]);function Fi({annotationName:e}){const t=Ei(e);return n(Di,{color:t})}const _i=m`
  border-radius: var(--ac-global-dimension-size-50);
  border: 1px solid var(--ac-global-color-grey-400);
  padding: var(--ac-global-dimension-size-50)
    var(--ac-global-dimension-size-100);
  transition: background-color 0.2s;
  &:hover {
    background-color: var(--ac-global-color-grey-300);
  }
  .ac-icon-wrap {
    font-size: 12px;
  }
`,En=m`
  display: flex;
  align-items: center;
  .ac-text {
    display: inline-block;
    max-width: 9rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
`,Pi=(e,t)=>{switch(t){case"label":return e.label||typeof e.score=="number"&&me(e.score)||"n/a";case"score":return typeof e.score=="number"&&me(e.score)||e.label||"n/a";default:P()}};function O1({annotation:e,onClick:t,annotationDisplayPreference:a="score"}){const r=typeof t=="function",i=Pi(e,a);return n("div",{role:r?"button":void 0,css:m(_i,r&&"cursor: pointer;"),"aria-label":r?"Click to view the annotation trace":`Annotation: ${e.name}`,onClick:l=>{l.stopPropagation(),l.preventDefault(),t&&t()},children:s(D,{direction:"row",gap:"size-100",alignItems:"center",children:[n(Fi,{annotationName:e.name}),n("div",{css:En,children:n(C,{weight:"heavy",textSize:"small",color:"inherit",children:e.name})}),n("div",{css:m(En,m`
              margin-left: var(--ac-global-dimension-100);
            `),children:n(C,{textSize:"small",children:i})}),r?n(I,{svg:n(w.ArrowIosForwardOutline,{})}):null]})})}function A1({annotation:e,children:t,extra:a,layout:r="vertical",width:i}){return s(A,{delay:500,offset:3,children:[n(q,{children:t}),n(ya,{UNSAFE_style:{minWidth:i},children:s(D,{direction:r==="horizontal"?"row":"column",alignItems:"center",children:[s(R,{children:[n(C,{weight:"heavy",color:"inherit",textSize:"large",elementType:"h3",children:e.name}),s(R,{paddingTop:"size-50",minWidth:"150px",children:[s(D,{direction:"row",justifyContent:"space-between",children:[n(C,{weight:"heavy",color:"inherit",children:"label"}),n(C,{color:"inherit",children:e.label||"--"})]}),s(D,{direction:"row",justifyContent:"space-between",children:[n(C,{weight:"heavy",color:"inherit",children:"score"}),n(C,{color:"inherit",children:mt(e.score)})]}),e.annotatorKind?s(D,{direction:"row",justifyContent:"space-between",children:[n(C,{weight:"heavy",color:"inherit",children:"annotator kind"}),n(C,{color:"inherit",children:e.annotatorKind})]}):null]}),e.explanation?n(R,{paddingTop:"size-50",children:s(D,{direction:"column",children:[n(C,{weight:"heavy",color:"inherit",children:"explanation"}),n(R,{maxHeight:"300px",overflow:"auto",children:n(C,{color:"inherit",children:e.explanation})})]})}):null]}),a]})})]})}function Vi({latencyMs:e,textSize:t="medium",showIcon:a=!0}){const r=p.useMemo(()=>e<3e3?"green-1200":e<8e3?"yellow-1200":e<12e3?"orange-1200":"red-1200",[e]),i=p.useMemo(()=>e<10?me(e)+"ms":me(e/1e3)+"s",[e]);return s(D,{direction:"row",alignItems:"center",justifyContent:"start",gap:"size-50",children:[a?n(C,{color:r,textSize:t,children:n(I,{svg:n(w.ClockOutline,{})})}):null,n(C,{color:r,textSize:t,children:i})]})}function Ni(e){switch(e){case"OK":return"success";case"ERROR":return"danger";case"UNSET":return"grey-500";default:P()}}function Ri({statusCode:e}){let t=n(w.MinusCircleOutline,{});const a=Ni(e);switch(e){case"OK":t=n(w.CheckmarkCircleOutline,{});break;case"ERROR":t=n(w.AlertCircleOutline,{});break;case"UNSET":t=n(w.MinusCircleOutline,{});break;default:P()}return n(I,{svg:t,color:a,"aria-label":e})}function Oi(e){return s(A,{children:[n(q,{children:n(Ze,{textSize:e.textSize,children:e.tokenCountTotal})}),n(Q,{children:s(D,{direction:"column",gap:"size-50",children:[s(D,{direction:"row",gap:"size-100",justifyContent:"space-between",children:["prompt tokens",n(Ze,{children:e.tokenCountPrompt})]}),s(D,{direction:"row",gap:"size-100",justifyContent:"space-between",children:["completion tokens",n(Ze,{children:e.tokenCountCompletion})]})]})})]})}function Ze({children:e,...t}){return s(D,{direction:"row",gap:"size-50",alignItems:"center",children:[n(I,{svg:n(w.TokensOutline,{}),css:m`
          color: var(--ac-global-text-color-900);
        `}),n(C,{...t,children:e})]})}const Ai=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("mask",{id:"path-2-inside-1_33_16916",fill:"currentColor",children:n("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M13 8C13 8.64491 12.8779 9.2613 12.6556 9.82732L17.1924 14.3641L14.364 17.1926L9.82706 12.6557C9.26111 12.8779 8.64481 13 8 13C5.23858 13 3 10.7614 3 8C3 7.13361 3.22036 6.31869 3.60809 5.60822L6 8L7.5 7.50016L8 6.00016L5.60803 3.60819C6.31854 3.2204 7.13353 3 8 3C10.7614 3 13 5.23858 13 8Z"})}),n("path",{d:"M12.6556 9.82732L11.7248 9.46171L11.4853 10.0713L11.9485 10.5344L12.6556 9.82732ZM17.1924 14.3641L17.8995 15.0713L18.6066 14.3641L17.8995 13.657L17.1924 14.3641ZM14.364 17.1926L13.6569 17.8997L14.364 18.6068L15.0711 17.8997L14.364 17.1926ZM9.82706 12.6557L10.5342 11.9486L10.0711 11.4855L9.4615 11.7249L9.82706 12.6557ZM3.60809 5.60822L4.31518 4.90109L3.37037 3.95634L2.7303 5.12917L3.60809 5.60822ZM6 8L5.29291 8.70713L5.72988 9.14407L6.31613 8.94871L6 8ZM7.5 7.50016L7.81614 8.44888L8.29055 8.29079L8.44869 7.81639L7.5 7.50016ZM8 6.00016L8.94869 6.31639L9.14413 5.73007L8.70711 5.29306L8 6.00016ZM5.60803 3.60819L5.12895 2.73042L3.95616 3.37053L4.90093 4.3153L5.60803 3.60819ZM13.5863 10.1929C13.8537 9.51235 14 8.77206 14 8H12C12 8.51776 11.9021 9.01026 11.7248 9.46171L13.5863 10.1929ZM17.8995 13.657L13.3627 9.12022L11.9485 10.5344L16.4853 15.0713L17.8995 13.657ZM15.0711 17.8997L17.8995 15.0713L16.4853 13.657L13.6569 16.4855L15.0711 17.8997ZM9.11995 13.3628L13.6569 17.8997L15.0711 16.4855L10.5342 11.9486L9.11995 13.3628ZM8 14C8.77194 14 9.51211 13.8537 10.1926 13.5865L9.4615 11.7249C9.0101 11.9022 8.51768 12 8 12V14ZM2 8C2 11.3137 4.68629 14 8 14V12C5.79086 12 4 10.2091 4 8H2ZM2.7303 5.12917C2.2644 5.98288 2 6.96206 2 8H4C4 7.30516 4.17633 6.65449 4.48588 6.08727L2.7303 5.12917ZM6.70709 7.29287L4.31518 4.90109L2.901 6.31535L5.29291 8.70713L6.70709 7.29287ZM7.18387 6.55145L5.68387 7.05129L6.31613 8.94871L7.81614 8.44888L7.18387 6.55145ZM7.05132 5.68394L6.55132 7.18394L8.44869 7.81639L8.94869 6.31639L7.05132 5.68394ZM4.90093 4.3153L7.2929 6.70727L8.70711 5.29306L6.31514 2.90109L4.90093 4.3153ZM8 2C6.96197 2 5.98271 2.26444 5.12895 2.73042L6.08712 4.48596C6.65437 4.17636 7.3051 4 8 4V2ZM14 8C14 4.68629 11.3137 2 8 2V4C10.2091 4 12 5.79086 12 8H14Z",fill:"currentColor",fillOpacity:"0.9",mask:"url(#path-2-inside-1_33_16916)"})]}),Ki=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",fill:"currentColor",stroke:"currentColor"}),n("mask",{id:"path-2-inside-1_2321_643",fill:"white",children:n("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M13 8C13 8.64491 12.8779 9.2613 12.6556 9.82732L17.1924 14.3641L14.364 17.1926L9.82706 12.6557C9.26111 12.8779 8.64481 13 8 13C5.23858 13 3 10.7614 3 8C3 7.13361 3.22036 6.31869 3.60809 5.60822L6 8L7.5 7.50016L8 6.00016L5.60803 3.60819C6.31854 3.2204 7.13353 3 8 3C10.7614 3 13 5.23858 13 8Z"})}),n("path",{d:"M12.6556 9.82732L11.7248 9.46171L11.4853 10.0713L11.9485 10.5344L12.6556 9.82732ZM17.1924 14.3641L17.8995 15.0713L18.6066 14.3641L17.8995 13.657L17.1924 14.3641ZM14.364 17.1926L13.6569 17.8997L14.364 18.6068L15.0711 17.8997L14.364 17.1926ZM9.82706 12.6557L10.5342 11.9486L10.0711 11.4855L9.4615 11.7249L9.82706 12.6557ZM3.60809 5.60822L4.31518 4.90109L3.37037 3.95634L2.7303 5.12917L3.60809 5.60822ZM6 8L5.29291 8.70713L5.72988 9.14407L6.31613 8.94871L6 8ZM7.5 7.50016L7.81614 8.44888L8.29055 8.29079L8.44869 7.81639L7.5 7.50016ZM8 6.00016L8.94869 6.31639L9.14413 5.73007L8.70711 5.29306L8 6.00016ZM5.60803 3.60819L5.12895 2.73042L3.95616 3.37053L4.90093 4.3153L5.60803 3.60819ZM13.5863 10.1929C13.8537 9.51235 14 8.77206 14 8H12C12 8.51776 11.9021 9.01026 11.7248 9.46171L13.5863 10.1929ZM17.8995 13.657L13.3627 9.12022L11.9485 10.5344L16.4853 15.0713L17.8995 13.657ZM15.0711 17.8997L17.8995 15.0713L16.4853 13.657L13.6569 16.4855L15.0711 17.8997ZM9.11995 13.3628L13.6569 17.8997L15.0711 16.4855L10.5342 11.9486L9.11995 13.3628ZM8 14C8.77194 14 9.51211 13.8537 10.1926 13.5865L9.4615 11.7249C9.0101 11.9022 8.51768 12 8 12V14ZM2 8C2 11.3137 4.68629 14 8 14V12C5.79086 12 4 10.2091 4 8H2ZM2.7303 5.12917C2.2644 5.98288 2 6.96206 2 8H4C4 7.30516 4.17633 6.65449 4.48588 6.08727L2.7303 5.12917ZM6.70709 7.29287L4.31518 4.90109L2.901 6.31535L5.29291 8.70713L6.70709 7.29287ZM7.18387 6.55145L5.68387 7.05129L6.31613 8.94871L7.81614 8.44888L7.18387 6.55145ZM7.05132 5.68394L6.55132 7.18394L8.44869 7.81639L8.94869 6.31639L7.05132 5.68394ZM4.90093 4.3153L7.2929 6.70727L8.70711 5.29306L6.31514 2.90109L4.90093 4.3153ZM8 2C6.96197 2 5.98271 2.26444 5.12895 2.73042L6.08712 4.48596C6.65437 4.17636 7.3051 4 8 4V2ZM14 8C14 4.68629 11.3137 2 8 2V4C10.2091 4 12 5.79086 12 8H14Z",fill:"black",mask:"url(#path-2-inside-1_2321_643)"})]}),zi=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("path",{d:"M4.43782 6.78868L10 3.57735L15.5622 6.78868V13.2113L10 16.4226L4.43782 13.2113V6.78868Z",stroke:"currentColor",strokeOpacity:"0.9"})]}),$i=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",fill:"currentColor",stroke:"currentColor"}),n("path",{d:"M4.43782 6.78868L10 3.57735L15.5622 6.78868V13.2113L10 16.4226L4.43782 13.2113V6.78868Z",stroke:"black"})]}),Gi=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("path",{d:"M5 16C5 16 5 11 10 11C15 11 15 16 15 16",stroke:"currentColor",strokeOpacity:"0.9"}),n("rect",{x:"6.5",y:"4.5",width:"7",height:"5",rx:"0.5",stroke:"currentColor",strokeOpacity:"0.9"})]}),Bi=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{width:"20",height:"20",rx:"4",fill:"currentColor"}),n("path",{d:"M10 11C5 11 5 16 5 16H15C15 16 15 11 10 11Z",stroke:"black"}),n("rect",{x:"6.5",y:"4.5",width:"7",height:"5",rx:"0.5",stroke:"black"})]}),Qi=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M10 6C10 7.10457 9.10457 8 8 8C6.89543 8 6 7.10457 6 6C6 4.89543 6.89543 4 8 4C9.10457 4 10 4.89543 10 6ZM10.0558 8.18487C9.51887 8.6903 8.7956 9 8 9C7.91155 9 7.824 8.99617 7.7375 8.98867L7.10304 11.2093C8.21409 11.6488 9 12.7326 9 14C9 15.6569 7.65685 17 6 17C4.34315 17 3 15.6569 3 14C3 12.3431 4.34315 11 6 11C6.0409 11 6.08161 11.0008 6.12212 11.0024L6.76944 8.73682C5.72625 8.26703 5 7.21833 5 6C5 4.34315 6.34315 3 8 3C9.65685 3 11 4.34315 11 6C11 6.50075 10.8773 6.97285 10.6604 7.38788L12.1873 8.6094C12.6908 8.22697 13.3189 8 14 8C15.6569 8 17 9.34315 17 11C17 12.6569 15.6569 14 14 14C12.3431 14 11 12.6569 11 11C11 10.3864 11.1842 9.81579 11.5004 9.34053L10.0558 8.18487ZM16 11C16 12.1046 15.1046 13 14 13C12.8954 13 12 12.1046 12 11C12 9.89543 12.8954 9 14 9C15.1046 9 16 9.89543 16 11ZM6 16C7.10457 16 8 15.1046 8 14C8 12.8954 7.10457 12 6 12C4.89543 12 4 12.8954 4 14C4 15.1046 4.89543 16 6 16Z",fill:"currentColor",fillOpacity:"0.9"})]}),Ui=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",fill:"currentColor",stroke:"currentColor"}),n("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M10 6.00003C10 7.1046 9.10457 8.00003 8 8.00003C6.89543 8.00003 6 7.1046 6 6.00003C6 4.89546 6.89543 4.00003 8 4.00003C9.10457 4.00003 10 4.89546 10 6.00003ZM10.0558 8.1849C9.51887 8.69033 8.7956 9.00003 8 9.00003C7.91155 9.00003 7.824 8.9962 7.7375 8.9887L7.10304 11.2093C8.21409 11.6488 9 12.7326 9 14C9 15.6569 7.65685 17 6 17C4.34315 17 3 15.6569 3 14C3 12.3432 4.34315 11 6 11C6.0409 11 6.08161 11.0008 6.12212 11.0025L6.76944 8.73685C5.72625 8.26706 5 7.21836 5 6.00003C5 4.34318 6.34315 3.00003 8 3.00003C9.65685 3.00003 11 4.34318 11 6.00003C11 6.50078 10.8773 6.97288 10.6604 7.38791L12.1873 8.60943C12.6908 8.227 13.3189 8.00003 14 8.00003C15.6569 8.00003 17 9.34318 17 11C17 12.6569 15.6569 14 14 14C12.3431 14 11 12.6569 11 11C11 10.3864 11.1842 9.81582 11.5004 9.34056L10.0558 8.1849ZM16 11C16 12.1046 15.1046 13 14 13C12.8954 13 12 12.1046 12 11C12 9.89546 12.8954 9.00003 14 9.00003C15.1046 9.00003 16 9.89546 16 11ZM6 16C7.10457 16 8 15.1046 8 14C8 12.8955 7.10457 12 6 12C4.89543 12 4 12.8955 4 14C4 15.1046 4.89543 16 6 16Z",fill:"black"})]}),Hi=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("path",{d:"M14.65 6.5C14.65 6.98637 14.2466 7.52091 13.379 7.95472C12.5323 8.37806 11.3382 8.65 10 8.65C8.66184 8.65 7.46767 8.37806 6.62099 7.95472C5.75338 7.52091 5.35 6.98637 5.35 6.5C5.35 6.01363 5.75338 5.47909 6.62099 5.04528C7.46767 4.62194 8.66184 4.35 10 4.35C11.3382 4.35 12.5323 4.62194 13.379 5.04528C14.2466 5.47909 14.65 6.01363 14.65 6.5Z",stroke:"currentColor",strokeOpacity:"0.9",strokeWidth:"0.7"}),n("path",{d:"M14.6875 6.83482V9.62479C14.6875 9.62479 13.0769 11.1873 10 11.1873C6.92308 11.1873 5.3125 9.62479 5.3125 9.62479V6.7437",stroke:"currentColor",strokeOpacity:"0.9",strokeWidth:"0.7"}),n("path",{d:"M14.6875 9.625V12.125C14.6875 12.125 13.0769 13.6875 10 13.6875C6.92308 13.6875 5.3125 12.125 5.3125 12.125V9.625",stroke:"currentColor",strokeOpacity:"0.9",strokeWidth:"0.7"}),n("path",{d:"M14.6875 12.125V14.625C14.6875 14.625 13.0769 16.1875 10 16.1875C6.92308 16.1875 5.3125 14.625 5.3125 14.625V12.125",stroke:"currentColor",strokeOpacity:"0.9",strokeWidth:"0.7"})]}),Zi=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",fill:"currentColor",stroke:"currentColor"}),n("path",{d:"M14.65 6.5C14.65 6.98637 14.2466 7.52091 13.379 7.95472C12.5323 8.37806 11.3382 8.65 10 8.65C8.66184 8.65 7.46767 8.37806 6.62099 7.95472C5.75338 7.52091 5.35 6.98637 5.35 6.5C5.35 6.01363 5.75338 5.47909 6.62099 5.04528C7.46767 4.62194 8.66184 4.35 10 4.35C11.3382 4.35 12.5323 4.62194 13.379 5.04528C14.2466 5.47909 14.65 6.01363 14.65 6.5Z",stroke:"black",strokeWidth:"0.7"}),n("path",{d:"M14.6875 6.83504V9.625C14.6875 9.625 13.0769 11.1875 10 11.1875C6.92308 11.1875 5.3125 9.625 5.3125 9.625V6.74392",stroke:"black",strokeWidth:"0.7"}),n("path",{d:"M14.6875 9.625V12.125C14.6875 12.125 13.0769 13.6875 10 13.6875C6.92308 13.6875 5.3125 12.125 5.3125 12.125V9.625",stroke:"black",strokeWidth:"0.7"}),n("path",{d:"M14.6875 12.125V14.625C14.6875 14.625 13.0769 16.1875 10 16.1875C6.92308 16.1875 5.3125 14.625 5.3125 14.625V12.125",stroke:"black",strokeWidth:"0.7"})]}),ji=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor"}),n("path",{d:"M4.5359 10L8 4L11.4641 10H4.5359Z",stroke:"currentColor"}),n("path",{d:"M8.5359 10L12 16L15.4641 10H8.5359Z",stroke:"currentColor"})]}),qi=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",fill:"currentColor",stroke:"currentColor"}),n("path",{d:"M4.5359 10L8 4L11.4641 10H4.5359Z",stroke:"black"}),n("path",{d:"M8.5359 10L12 16L15.4641 10H8.5359Z",stroke:"black"})]}),Wi=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M10 15C12.7614 15 15 12.7614 15 10C15 7.23858 12.7614 5 10 5C7.23858 5 5 7.23858 5 10C5 12.7614 7.23858 15 10 15ZM10 16C13.3137 16 16 13.3137 16 10C16 6.68629 13.3137 4 10 4C6.68629 4 4 6.68629 4 10C4 13.3137 6.68629 16 10 16Z",fill:"currentColor",fillOpacity:"0.9"})]}),Ji=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",fill:"currentColor",stroke:"currentColor"}),n("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M10 15C12.7614 15 15 12.7614 15 10C15 7.23858 12.7614 5 10 5C7.23858 5 5 7.23858 5 10C5 12.7614 7.23858 15 10 15ZM10 16C13.3137 16 16 13.3137 16 10C16 6.68629 13.3137 4 10 4C6.68629 4 4 6.68629 4 10C4 13.3137 6.68629 16 10 16Z",fill:"black"})]}),Xi=()=>n("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"})}),Yi=()=>n("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",fill:"currentColor",stroke:"currentColor"})}),el=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor"}),n("path",{d:"M14.4254 5.58523L15.744 6.87427L15.7249 6.89333L15.7043 6.91394L15.6837 6.93453L15.6631 6.95509L15.6425 6.97562L15.622 6.99612L15.6015 7.01659L15.581 7.03703L15.5606 7.05745L15.5402 7.07783L15.5198 7.09819L15.4995 7.11852L15.4791 7.13882L15.4588 7.15909L15.4386 7.17934L15.4183 7.19956L15.3981 7.21974L15.3779 7.23991L15.3578 7.26004L15.3377 7.28015L15.3176 7.30022L15.2975 7.32028L15.2774 7.3403L15.2574 7.3603L15.2374 7.38027L15.2175 7.40021L15.1975 7.42013L15.1776 7.44002L15.1577 7.45988L15.1379 7.47972L15.118 7.49953L15.0982 7.51931L15.0784 7.53907L15.0587 7.5588L15.0389 7.57851L15.0192 7.59819L14.9996 7.61785L14.9799 7.63748L14.9603 7.65708L14.9407 7.67666L14.9211 7.69621L14.9016 7.71574L14.882 7.73524L14.8625 7.75472L14.8431 7.77417L14.8236 7.7936L14.8042 7.81301L14.7848 7.83239L14.7654 7.85174L14.746 7.87107L14.7267 7.89038L14.7074 7.90966L14.6881 7.92892L14.6689 7.94815L14.6496 7.96736L14.6304 7.98655L14.6113 8.00571L14.5921 8.02485L14.573 8.04397L14.5538 8.06306L14.5347 8.08213L14.5157 8.10118L14.4966 8.1202L14.4776 8.1392L14.4586 8.15818L14.4396 8.17714L14.4207 8.19607L14.4017 8.21498L14.3828 8.23387L14.3639 8.25274L14.3451 8.27158L14.3262 8.2904L14.3074 8.3092L14.2886 8.32798L14.2698 8.34674L14.2511 8.36547L14.2323 8.38418L14.2136 8.40288L14.1949 8.42155L14.1763 8.4402L14.1576 8.45883L14.139 8.47743L14.1204 8.49602L14.1018 8.51459L14.0832 8.53313L14.0647 8.55166L14.0462 8.57016L14.0277 8.58864L14.0092 8.60711L13.9907 8.62555L13.9723 8.64397L13.9538 8.66238L13.9354 8.68076L13.917 8.69913L13.8987 8.71747L13.8803 8.73579L13.862 8.7541L13.8437 8.77239L13.8254 8.79065L13.8071 8.8089L13.7889 8.82713L13.7707 8.84534L13.7524 8.86353L13.7343 8.8817L13.7161 8.89986L13.6979 8.91799L13.6798 8.93611L13.6617 8.95421L13.6436 8.97229L13.6255 8.99036L13.6074 9.0084L13.5894 9.02643L13.5713 9.04444L13.5533 9.06243L13.5353 9.0804L13.5173 9.09836L13.4994 9.1163L13.4814 9.13422L13.4635 9.15213L13.4456 9.17002L13.4277 9.18789L13.4098 9.20574L13.392 9.22358L13.3741 9.2414L13.3563 9.25921L13.3385 9.277L13.3207 9.29477L13.3029 9.31253L13.2852 9.33027L13.2674 9.34799L13.2497 9.3657L13.232 9.38339L13.2143 9.40107L13.1966 9.41873L13.1789 9.43638L13.1613 9.45401L13.1436 9.47163L13.126 9.48923L13.1084 9.50681L13.0908 9.52438L13.0733 9.54194L13.0557 9.55948L13.0381 9.57701L13.0206 9.59452L13.0031 9.61202L12.9856 9.6295L12.9681 9.64697L12.9506 9.66443L12.9332 9.68187L12.9157 9.6993L12.8983 9.71671L12.8809 9.73412L12.8634 9.7515L12.8461 9.76888L12.8287 9.78624L12.8113 9.80358L12.794 9.82092L12.7766 9.83824L12.7593 9.85555L12.742 9.87284L12.7247 9.89013L12.7074 9.9074L12.6901 9.92466L12.6728 9.9419L12.6556 9.95913L12.6383 9.97636L12.6211 9.99356L12.6039 10.0108L12.5867 10.0279L12.5695 10.0451L12.5523 10.0623L12.5351 10.0794L12.518 10.0966L12.5008 10.1137L12.4837 10.1308L12.4666 10.1479L12.4495 10.165L12.4324 10.1821L12.4153 10.1992L12.3982 10.2162L12.3811 10.2333L12.364 10.2503L12.347 10.2674L12.33 10.2844L12.3129 10.3014L12.2959 10.3184L12.2789 10.3354L12.2619 10.3524L12.2449 10.3693L12.2279 10.3863L12.211 10.4032L12.194 10.4202L12.177 10.4371L12.1601 10.454L12.1432 10.471L12.1262 10.4879L12.1093 10.5048L12.0924 10.5216L12.0755 10.5385L12.0586 10.5554L12.0417 10.5723L12.0249 10.5891L12.008 10.606L11.9911 10.6228L11.9743 10.6396L11.9575 10.6565L11.9406 10.6733L11.9238 10.6901L11.907 10.7069L11.8902 10.7237L11.8734 10.7404L11.8566 10.7572L11.8398 10.774L11.823 10.7907L11.8062 10.8075L11.7895 10.8243L11.7727 10.841L11.7559 10.8577L11.7392 10.8745L11.7225 10.8912L11.7057 10.9079L11.689 10.9246L11.6723 10.9413L11.6556 10.958L11.6389 10.9747L11.6221 10.9914L11.6054 11.0081L11.5888 11.0247L11.5721 11.0414L11.5554 11.0581L11.5387 11.0747L11.522 11.0914L11.5054 11.108L11.4887 11.1247L11.4721 11.1413L11.4554 11.1579L11.4388 11.1746L11.4221 11.1912L11.4055 11.2078L11.3888 11.2244L11.3722 11.241L11.3556 11.2576L11.339 11.2742L11.3224 11.2908L11.3057 11.3074L11.2891 11.324L11.2725 11.3406L11.2559 11.3572L11.2393 11.3738L11.2227 11.3903L11.2061 11.4069L11.1895 11.4235L11.173 11.44L11.1564 11.4566L11.1398 11.4732L11.1232 11.4897L11.1066 11.5063L11.0901 11.5228L11.0735 11.5394L11.0569 11.5559L11.0404 11.5725L11.0238 11.589L11.0072 11.6056L10.9907 11.6221L10.9741 11.6386L10.9576 11.6552L10.941 11.6717L10.9245 11.6883L10.9079 11.7048L10.8914 11.7213L10.8748 11.7378L10.8583 11.7544L10.8417 11.7709L10.8252 11.7874L10.8086 11.804L10.7921 11.8205L10.7755 11.837L10.759 11.8535L10.7424 11.8701L10.7259 11.8866L10.7094 11.9031L10.6928 11.9196L10.6763 11.9362L10.6597 11.9527L10.6432 11.9692L10.6266 11.9857L10.6101 12.0023L10.5935 12.0188L10.577 12.0353L10.5604 12.0519L10.5439 12.0684L10.5273 12.0849L10.5108 12.1015L10.4942 12.118L10.4777 12.1345L10.4611 12.1511L10.4446 12.1676L10.428 12.1841L10.4114 12.2007L10.3949 12.2172L10.3783 12.2338L10.3618 12.2503L10.3452 12.2669L10.3286 12.2834L10.312 12.3L10.2955 12.3165L10.2789 12.3331L10.2623 12.3497L10.2457 12.3662L10.2291 12.3828L10.2125 12.3994L10.1959 12.4159L10.1793 12.4325L10.1627 12.4491L10.1461 12.4657L10.1295 12.4823L10.1129 12.4989L10.0963 12.5155L10.0797 12.5321L10.0631 12.5487L10.0464 12.5653L10.0298 12.5819L10.0132 12.5985L9.99652 12.6151L9.97987 12.6318L9.96322 12.6484L9.94657 12.665L9.92991 12.6817L9.91324 12.6983L9.89657 12.715L9.87989 12.7316L9.86321 12.7483L9.84653 12.7649L9.82984 12.7816L9.81314 12.7983L9.79644 12.815L9.77973 12.8317L9.76301 12.8484L9.74629 12.8651L9.72957 12.8818L9.71283 12.8985L9.69609 12.9152L9.67935 12.9319L9.6626 12.9487L9.64584 12.9654L9.62907 12.9822L9.6123 12.9989L9.59552 13.0157L9.57873 13.0324L9.56194 13.0492L9.54514 13.066L9.52833 13.0828L9.51151 13.0996L9.49469 13.1164L9.47786 13.1332L9.46102 13.15L9.44417 13.1668L9.42732 13.1837L9.41045 13.2005L9.39358 13.2174L9.3767 13.2342L9.35981 13.2511L9.34292 13.268L9.32601 13.2849L9.3091 13.3018L9.29217 13.3187L9.27524 13.3356L9.2583 13.3525L9.24135 13.3694L9.22439 13.3864L9.20742 13.4033L9.19044 13.4203L9.17345 13.4372L9.15645 13.4542L9.13945 13.4712L9.12243 13.4882L9.1054 13.5052L9.08836 13.5222L9.07131 13.5393L9.05426 13.5563L9.03719 13.5734L9.02011 13.5904L9.00302 13.6075L8.98592 13.6246L8.9688 13.6417L8.95168 13.6588L8.93455 13.6759L8.9174 13.693L8.90024 13.7101L8.88308 13.7273L8.8659 13.7444L8.84871 13.7616L8.8315 13.7788L8.81429 13.796L8.79706 13.8132L8.77983 13.8304L8.76257 13.8477L8.74531 13.8649L8.72804 13.8821L8.71075 13.8994L8.69345 13.9167L8.67614 13.934L8.65881 13.9513L8.64147 13.9686L8.62412 13.9859L8.60676 14.0033L8.58938 14.0206L8.57199 14.038L8.55458 14.0554L8.53716 14.0728L8.51973 14.0902L8.50229 14.1076L8.48483 14.1251L8.46736 14.1425L8.44987 14.16L8.43237 14.1775L8.41485 14.195L8.39732 14.2125L8.37978 14.23L8.36222 14.2475L8.34465 14.2651L8.32706 14.2827L8.30945 14.3002L8.29184 14.3178L8.2742 14.3355L8.25656 14.3531L8.23889 14.3707L8.22121 14.3884L8.20352 14.4061L8.18581 14.4238L8.16808 14.4415L8.15034 14.4592L8.13258 14.4769L8.11481 14.4947L8.09702 14.5124L8.07921 14.5302L8.06139 14.548L8.04355 14.5658L8.0257 14.5837L8.00783 14.6015L7.98994 14.6194L7.97203 14.6373L7.95411 14.6552L7.93617 14.6731L7.91821 14.691L7.90024 14.709L7.88225 14.727L7.86424 14.7449L7.84621 14.763L7.82817 14.781L7.81011 14.799L7.79203 14.8171L7.77393 14.8352L7.75581 14.8533L7.73768 14.8714L7.71952 14.8895L7.70135 14.9076L7.68316 14.9258L7.66495 14.944L7.64673 14.9622L7.62848 14.9804L7.61022 14.9987L7.59193 15.0169L7.57363 15.0352L7.55531 15.0535L7.53697 15.0718L7.5186 15.0902L7.50022 15.1085L7.48182 15.1269L7.4634 15.1453L7.44496 15.1637L7.4265 15.1822L7.40802 15.2006L7.38952 15.2191L7.371 15.2376L7.35246 15.2561L7.33389 15.2747L7.31531 15.2932L7.29671 15.3118L7.27808 15.3304L7.25944 15.3491L7.24077 15.3677L7.22208 15.3864L7.20337 15.4051L7.18464 15.4238L7.16589 15.4425L7.14712 15.4612L7.12832 15.48L7.10951 15.4988L7.09067 15.5176L7.07181 15.5365L7.05292 15.5553L7.03402 15.5742L7.01509 15.5931L6.99614 15.612C6.27167 16.3357 5.09652 16.3361 4.37259 15.613C3.64838 14.8896 3.64838 13.7168 4.37259 12.9935L13.1214 4.2547L14.4178 5.57764L14.4177 5.57772L14.4254 5.58523Z",stroke:"currentColor"}),n("path",{d:"M12.5299 10.2848L7.32791 15.5545C7.12956 15.7555 6.88934 15.9156 6.62689 16.0225C6.08679 16.2424 5.46752 16.2239 4.94171 15.972L4.77945 16.31L4.94171 15.972C4.6339 15.8246 4.36574 15.6007 4.16736 15.3245L4.02179 15.1219C3.60142 14.5367 3.60138 13.749 4.02169 13.1637C4.12291 13.0228 4.24539 12.8984 4.38476 12.7949L5.72374 11.8006L5.76816 11.7676L5.80115 11.7232L5.91056 11.576C6.30572 11.0443 6.96187 10.4244 7.58765 10.0864C7.90229 9.91646 8.17215 9.83813 8.37711 9.84461C8.55555 9.85025 8.69852 9.9179 8.81563 10.1071C8.88186 10.2141 8.92418 10.3701 8.97238 10.5823C8.97507 10.5942 8.9778 10.6063 8.98058 10.6186C9.00013 10.7052 9.02201 10.8022 9.04751 10.8896C9.07575 10.9865 9.11828 11.1086 9.19239 11.2146C9.29475 11.361 9.4504 11.4075 9.53763 11.4247C9.63768 11.4444 9.74477 11.4446 9.84616 11.436C10.0516 11.4187 10.299 11.3594 10.5607 11.2642C11.0498 11.0864 11.6345 10.7668 12.1516 10.2848L12.5299 10.2848Z",stroke:"currentColor",strokeWidth:"0.75"})]}),nl=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",fill:"currentColor",stroke:"currentColor"}),n("path",{d:"M14.4254 5.58523L15.744 6.87427L15.7249 6.89333L15.7043 6.91394L15.6837 6.93453L15.6631 6.95509L15.6425 6.97562L15.622 6.99612L15.6015 7.01659L15.581 7.03703L15.5606 7.05745L15.5402 7.07783L15.5198 7.09819L15.4995 7.11852L15.4791 7.13882L15.4588 7.15909L15.4386 7.17934L15.4183 7.19956L15.3981 7.21974L15.3779 7.23991L15.3578 7.26004L15.3377 7.28015L15.3176 7.30022L15.2975 7.32028L15.2774 7.3403L15.2574 7.3603L15.2374 7.38027L15.2175 7.40021L15.1975 7.42013L15.1776 7.44002L15.1577 7.45988L15.1379 7.47972L15.118 7.49953L15.0982 7.51931L15.0784 7.53907L15.0587 7.5588L15.0389 7.57851L15.0192 7.59819L14.9996 7.61785L14.9799 7.63748L14.9603 7.65708L14.9407 7.67666L14.9211 7.69621L14.9016 7.71574L14.882 7.73524L14.8625 7.75472L14.8431 7.77417L14.8236 7.7936L14.8042 7.81301L14.7848 7.83239L14.7654 7.85174L14.746 7.87107L14.7267 7.89038L14.7074 7.90966L14.6881 7.92892L14.6689 7.94815L14.6496 7.96736L14.6304 7.98655L14.6113 8.00571L14.5921 8.02485L14.573 8.04397L14.5538 8.06306L14.5347 8.08213L14.5157 8.10118L14.4966 8.1202L14.4776 8.1392L14.4586 8.15818L14.4396 8.17714L14.4207 8.19607L14.4017 8.21498L14.3828 8.23387L14.3639 8.25274L14.3451 8.27158L14.3262 8.2904L14.3074 8.3092L14.2886 8.32798L14.2698 8.34674L14.2511 8.36547L14.2323 8.38418L14.2136 8.40288L14.1949 8.42155L14.1763 8.4402L14.1576 8.45883L14.139 8.47743L14.1204 8.49602L14.1018 8.51459L14.0832 8.53313L14.0647 8.55166L14.0462 8.57016L14.0277 8.58864L14.0092 8.60711L13.9907 8.62555L13.9723 8.64397L13.9538 8.66238L13.9354 8.68076L13.917 8.69913L13.8987 8.71747L13.8803 8.73579L13.862 8.7541L13.8437 8.77239L13.8254 8.79065L13.8071 8.8089L13.7889 8.82713L13.7707 8.84534L13.7524 8.86353L13.7343 8.8817L13.7161 8.89986L13.6979 8.91799L13.6798 8.93611L13.6617 8.95421L13.6436 8.97229L13.6255 8.99036L13.6074 9.0084L13.5894 9.02643L13.5713 9.04444L13.5533 9.06243L13.5353 9.0804L13.5173 9.09836L13.4994 9.1163L13.4814 9.13422L13.4635 9.15213L13.4456 9.17002L13.4277 9.18789L13.4098 9.20574L13.392 9.22358L13.3741 9.2414L13.3563 9.25921L13.3385 9.277L13.3207 9.29477L13.3029 9.31253L13.2852 9.33027L13.2674 9.34799L13.2497 9.3657L13.232 9.38339L13.2143 9.40107L13.1966 9.41873L13.1789 9.43638L13.1613 9.45401L13.1436 9.47163L13.126 9.48923L13.1084 9.50681L13.0908 9.52438L13.0733 9.54194L13.0557 9.55948L13.0381 9.57701L13.0206 9.59452L13.0031 9.61202L12.9856 9.6295L12.9681 9.64697L12.9506 9.66443L12.9332 9.68187L12.9157 9.6993L12.8983 9.71671L12.8809 9.73412L12.8634 9.7515L12.8461 9.76888L12.8287 9.78624L12.8113 9.80358L12.794 9.82092L12.7766 9.83824L12.7593 9.85555L12.742 9.87284L12.7247 9.89013L12.7074 9.9074L12.6901 9.92466L12.6728 9.9419L12.6556 9.95913L12.6383 9.97636L12.6211 9.99356L12.6039 10.0108L12.5867 10.0279L12.5695 10.0451L12.5523 10.0623L12.5351 10.0794L12.518 10.0966L12.5008 10.1137L12.4837 10.1308L12.4666 10.1479L12.4495 10.165L12.4324 10.1821L12.4153 10.1992L12.3982 10.2162L12.3811 10.2333L12.364 10.2503L12.347 10.2674L12.33 10.2844L12.3129 10.3014L12.2959 10.3184L12.2789 10.3354L12.2619 10.3524L12.2449 10.3693L12.2279 10.3863L12.211 10.4032L12.194 10.4202L12.177 10.4371L12.1601 10.454L12.1432 10.471L12.1262 10.4879L12.1093 10.5048L12.0924 10.5216L12.0755 10.5385L12.0586 10.5554L12.0417 10.5723L12.0249 10.5891L12.008 10.606L11.9911 10.6228L11.9743 10.6396L11.9575 10.6565L11.9406 10.6733L11.9238 10.6901L11.907 10.7069L11.8902 10.7237L11.8734 10.7404L11.8566 10.7572L11.8398 10.774L11.823 10.7907L11.8062 10.8075L11.7895 10.8243L11.7727 10.841L11.7559 10.8577L11.7392 10.8745L11.7225 10.8912L11.7057 10.9079L11.689 10.9246L11.6723 10.9413L11.6556 10.958L11.6389 10.9747L11.6221 10.9914L11.6054 11.0081L11.5888 11.0247L11.5721 11.0414L11.5554 11.0581L11.5387 11.0747L11.522 11.0914L11.5054 11.108L11.4887 11.1247L11.4721 11.1413L11.4554 11.1579L11.4388 11.1746L11.4221 11.1912L11.4055 11.2078L11.3888 11.2244L11.3722 11.241L11.3556 11.2576L11.339 11.2742L11.3224 11.2908L11.3057 11.3074L11.2891 11.324L11.2725 11.3406L11.2559 11.3572L11.2393 11.3738L11.2227 11.3903L11.2061 11.4069L11.1895 11.4235L11.173 11.44L11.1564 11.4566L11.1398 11.4732L11.1232 11.4897L11.1066 11.5063L11.0901 11.5228L11.0735 11.5394L11.0569 11.5559L11.0404 11.5725L11.0238 11.589L11.0072 11.6056L10.9907 11.6221L10.9741 11.6386L10.9576 11.6552L10.941 11.6717L10.9245 11.6883L10.9079 11.7048L10.8914 11.7213L10.8748 11.7378L10.8583 11.7544L10.8417 11.7709L10.8252 11.7874L10.8086 11.804L10.7921 11.8205L10.7755 11.837L10.759 11.8535L10.7424 11.8701L10.7259 11.8866L10.7094 11.9031L10.6928 11.9196L10.6763 11.9362L10.6597 11.9527L10.6432 11.9692L10.6266 11.9857L10.6101 12.0023L10.5935 12.0188L10.577 12.0353L10.5604 12.0519L10.5439 12.0684L10.5273 12.0849L10.5108 12.1015L10.4942 12.118L10.4777 12.1345L10.4611 12.1511L10.4446 12.1676L10.428 12.1841L10.4114 12.2007L10.3949 12.2172L10.3783 12.2338L10.3618 12.2503L10.3452 12.2669L10.3286 12.2834L10.312 12.3L10.2955 12.3165L10.2789 12.3331L10.2623 12.3497L10.2457 12.3662L10.2291 12.3828L10.2125 12.3994L10.1959 12.4159L10.1793 12.4325L10.1627 12.4491L10.1461 12.4657L10.1295 12.4823L10.1129 12.4989L10.0963 12.5155L10.0797 12.5321L10.0631 12.5487L10.0464 12.5653L10.0298 12.5819L10.0132 12.5985L9.99652 12.6151L9.97987 12.6318L9.96322 12.6484L9.94657 12.665L9.92991 12.6817L9.91324 12.6983L9.89657 12.715L9.87989 12.7316L9.86321 12.7483L9.84653 12.7649L9.82984 12.7816L9.81314 12.7983L9.79644 12.815L9.77973 12.8317L9.76301 12.8484L9.74629 12.8651L9.72957 12.8818L9.71283 12.8985L9.69609 12.9152L9.67935 12.9319L9.6626 12.9487L9.64584 12.9654L9.62907 12.9822L9.6123 12.9989L9.59552 13.0157L9.57873 13.0324L9.56194 13.0492L9.54514 13.066L9.52833 13.0828L9.51151 13.0996L9.49469 13.1164L9.47786 13.1332L9.46102 13.15L9.44417 13.1668L9.42732 13.1837L9.41045 13.2005L9.39358 13.2174L9.3767 13.2342L9.35981 13.2511L9.34292 13.268L9.32601 13.2849L9.3091 13.3018L9.29217 13.3187L9.27524 13.3356L9.2583 13.3525L9.24135 13.3694L9.22439 13.3864L9.20742 13.4033L9.19044 13.4203L9.17345 13.4372L9.15645 13.4542L9.13945 13.4712L9.12243 13.4882L9.1054 13.5052L9.08836 13.5222L9.07131 13.5393L9.05426 13.5563L9.03719 13.5734L9.02011 13.5904L9.00302 13.6075L8.98592 13.6246L8.9688 13.6417L8.95168 13.6588L8.93455 13.6759L8.9174 13.693L8.90024 13.7101L8.88308 13.7273L8.8659 13.7444L8.84871 13.7616L8.8315 13.7788L8.81429 13.796L8.79706 13.8132L8.77983 13.8304L8.76257 13.8477L8.74531 13.8649L8.72804 13.8821L8.71075 13.8994L8.69345 13.9167L8.67614 13.934L8.65881 13.9513L8.64147 13.9686L8.62412 13.9859L8.60676 14.0033L8.58938 14.0206L8.57199 14.038L8.55458 14.0554L8.53716 14.0728L8.51973 14.0902L8.50229 14.1076L8.48483 14.1251L8.46736 14.1425L8.44987 14.16L8.43237 14.1775L8.41485 14.195L8.39732 14.2125L8.37978 14.23L8.36222 14.2475L8.34465 14.2651L8.32706 14.2827L8.30945 14.3002L8.29184 14.3178L8.2742 14.3355L8.25656 14.3531L8.23889 14.3707L8.22121 14.3884L8.20352 14.4061L8.18581 14.4238L8.16808 14.4415L8.15034 14.4592L8.13258 14.4769L8.11481 14.4947L8.09702 14.5124L8.07921 14.5302L8.06139 14.548L8.04355 14.5658L8.0257 14.5837L8.00783 14.6015L7.98994 14.6194L7.97203 14.6373L7.95411 14.6552L7.93617 14.6731L7.91821 14.691L7.90024 14.709L7.88225 14.727L7.86424 14.7449L7.84621 14.763L7.82817 14.781L7.81011 14.799L7.79203 14.8171L7.77393 14.8352L7.75581 14.8533L7.73768 14.8714L7.71952 14.8895L7.70135 14.9076L7.68316 14.9258L7.66495 14.944L7.64673 14.9622L7.62848 14.9804L7.61022 14.9987L7.59193 15.0169L7.57363 15.0352L7.55531 15.0535L7.53697 15.0718L7.5186 15.0902L7.50022 15.1085L7.48182 15.1269L7.4634 15.1453L7.44496 15.1637L7.4265 15.1822L7.40802 15.2006L7.38952 15.2191L7.371 15.2376L7.35246 15.2561L7.33389 15.2747L7.31531 15.2932L7.29671 15.3118L7.27808 15.3304L7.25944 15.3491L7.24077 15.3677L7.22208 15.3864L7.20337 15.4051L7.18464 15.4238L7.16589 15.4425L7.14712 15.4612L7.12832 15.48L7.10951 15.4988L7.09067 15.5176L7.07181 15.5365L7.05292 15.5553L7.03402 15.5742L7.01509 15.5931L6.99614 15.612C6.27167 16.3357 5.09652 16.3361 4.37259 15.613C3.64838 14.8896 3.64838 13.7168 4.37259 12.9935L13.1214 4.2547L14.4178 5.57764L14.4177 5.57772L14.4254 5.58523Z",stroke:"black"}),n("path",{d:"M12.5299 10.2849L7.32791 15.5546C7.12956 15.7556 6.88934 15.9156 6.62689 16.0225C6.08679 16.2425 5.46752 16.224 4.94171 15.9721L4.77945 16.31L4.94171 15.9721C4.6339 15.8246 4.36574 15.6008 4.16736 15.3246L4.02179 15.122C3.60142 14.5368 3.60138 13.749 4.02169 13.1638C4.12291 13.0229 4.24539 12.8984 4.38476 12.795L5.72374 11.8006L5.76816 11.7677L5.80115 11.7233L5.91056 11.5761C6.30572 11.0444 6.96187 10.4244 7.58765 10.0865C7.90229 9.91653 8.17215 9.83821 8.37711 9.84469C8.55555 9.85033 8.69852 9.91798 8.81563 10.1072C8.88186 10.2142 8.92418 10.3701 8.97238 10.5824C8.97507 10.5942 8.9778 10.6063 8.98058 10.6187C9.00013 10.7053 9.02201 10.8022 9.04751 10.8897C9.07575 10.9866 9.11828 11.1087 9.19239 11.2147C9.29475 11.3611 9.4504 11.4075 9.53763 11.4247C9.63768 11.4445 9.74477 11.4447 9.84616 11.4361C10.0516 11.4187 10.299 11.3594 10.5607 11.2643C11.0498 11.0864 11.6345 10.7669 12.1516 10.2849L12.5299 10.2849Z",stroke:"black",strokeWidth:"0.75"})]}),tl=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor"}),n("path",{d:"M15.4237 6.90042C15.5191 6.92315 15.6152 6.94413 15.7074 6.96092C15.7135 7.05035 15.7162 7.16454 15.7138 7.30375C15.7056 7.77188 15.6408 8.43317 15.515 9.1653C15.2592 10.6537 14.774 12.3014 14.1 13.2C13.4011 14.1319 12.332 14.9694 11.4101 15.584C10.9538 15.8882 10.5429 16.1317 10.2465 16.2989C10.1617 16.3467 10.0865 16.3882 10.0224 16.423C9.97538 16.3925 9.92211 16.3576 9.86327 16.3183C9.61299 16.1515 9.26304 15.908 8.86735 15.6037C8.07099 14.9911 7.11105 14.148 6.4 13.2C5.71286 12.2838 5.10686 10.6159 4.73507 9.12872C4.55136 8.39389 4.4322 7.73262 4.38844 7.26582C4.37726 7.14653 4.37171 7.04688 4.37029 6.96627C4.68202 6.91822 5.07002 6.82212 5.46167 6.6997C6.04643 6.51692 6.71066 6.25305 7.25513 5.93001C7.78069 5.61819 8.40348 5.00685 8.92133 4.49851C8.96063 4.45994 8.99932 4.42196 9.03732 4.38474C9.32127 4.10667 9.57222 3.86458 9.78023 3.69195C9.86978 3.61763 9.94141 3.56465 9.99619 3.52986C10.0511 3.56629 10.1228 3.62162 10.2126 3.69902C10.4221 3.8796 10.6732 4.13028 10.9589 4.41605L10.9643 4.42138C11.2419 4.69905 11.5471 5.00425 11.8469 5.27159C12.1431 5.53579 12.4648 5.79139 12.7764 5.94721C13.307 6.2125 13.989 6.47149 14.5895 6.66369C14.8912 6.76025 15.179 6.8421 15.4237 6.90042ZM9.92522 3.48908C9.92521 3.48905 9.92594 3.48931 9.92744 3.48994C9.92598 3.48943 9.92523 3.48911 9.92522 3.48908Z",stroke:"currentColor"})]}),al=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",fill:"currentColor",stroke:"currentColor"}),n("path",{d:"M9.92516 3.4891C9.92515 3.48907 9.92588 3.48933 9.92738 3.48997C9.92592 3.48946 9.92517 3.48914 9.92516 3.4891ZM9.99613 3.52989C10.051 3.56631 10.1227 3.62164 10.2125 3.69904C10.422 3.87963 10.6731 4.1303 10.9589 4.41608L10.9642 4.4214C11.2419 4.69907 11.5471 5.00428 11.8468 5.27161C12.1431 5.53582 12.4647 5.79142 12.7763 5.94724C13.3069 6.21253 13.9889 6.47151 14.5894 6.66371C14.8911 6.76027 15.179 6.84213 15.4236 6.90044C15.519 6.92317 15.6151 6.94416 15.7074 6.96095C15.7134 7.05037 15.7162 7.16456 15.7137 7.30377C15.7056 7.7719 15.6407 8.4332 15.5149 9.16533C15.2592 10.6537 14.7739 12.3014 14.0999 13.2C13.401 14.1319 12.3319 14.9694 11.4101 15.584C10.9538 15.8882 10.5428 16.1317 10.2465 16.2989C10.1617 16.3467 10.0864 16.3882 10.0223 16.423C9.97532 16.3925 9.92205 16.3576 9.86321 16.3184C9.61293 16.1515 9.26298 15.9081 8.86729 15.6037C8.07092 14.9911 7.11099 14.1481 6.39994 13.2C5.7128 12.2838 5.10679 10.6159 4.73501 9.12874C4.5513 8.39391 4.43214 7.73264 4.38838 7.26584C4.3772 7.14656 4.37164 7.0469 4.37023 6.9663C4.68196 6.91824 5.06996 6.82215 5.46161 6.69972C6.04637 6.51694 6.7106 6.25307 7.25507 5.93003C7.78063 5.61822 8.40342 5.00687 8.92127 4.49853C8.96057 4.45996 8.99926 4.42198 9.03726 4.38477C9.32121 4.1067 9.57216 3.8646 9.78016 3.69197C9.86972 3.61765 9.94135 3.56467 9.99613 3.52989Z",stroke:"black"})]});function rl({spanKind:e,variant:t="fill"}){const{theme:a}=U(),r=a==="dark",i=t==="fill";let l=i?n(Yi,{}):n(Xi,{}),o=r?"--ac-global-color-grey-600":"--ac-global-color-grey-500";switch(e){case"llm":o=r?"--ac-global-color-orange-1000":"--ac-global-color-orange-500",l=i?n($i,{}):n(zi,{});break;case"chain":o=r?"--ac-global-color-blue-1000":"--ac-global-color-blue-500",l=i?n(Ji,{}):n(Wi,{});break;case"retriever":o=r?"--ac-global-color-seafoam-1000":"--ac-global-color-seafoam-500",l=i?n(Zi,{}):n(Hi,{});break;case"embedding":o=r?"--ac-global-color-indigo-1000":"--ac-global-color-indigo-500",l=i?n(Ui,{}):n(Qi,{});break;case"agent":o=r?"--ac-global-text-color-900":"--ac-global-text-color-500",l=i?n(Bi,{}):n(Gi,{});break;case"tool":o=r?"--ac-global-color-yellow-1200":"--ac-global-color-yellow-500",l=i?n(Ki,{}):n(Ai,{});break;case"reranker":o=r?"--ac-global-color-celery-1000":"--ac-global-color-celery-500",l=i?n(qi,{}):n(ji,{});break;case"evaluator":o=r?"--ac-global-color-indigo-1000":"--ac-global-color-indigo-500",l=i?n(nl,{}):n(el,{});break;case"guardrail":o=r?"--ac-global-color-fuchsia-1200":"--ac-global-color-fuchsia-500",l=i?n(al,{}):n(tl,{});break}return n("div",{css:m`
        color: var(${o});
        width: 20px;
        height: 20px;
      `,title:e,children:l})}const yt=p.createContext(null);function vt(){const e=p.useContext(yt);if(e===null)throw new Error("useTraceTree must be used within a TraceTreeProvider");return e}function il(e){const[t,a]=p.useState(!1),r=p.useCallback(i=>{p.startTransition(()=>{a(i)})},[]);return n(yt.Provider,{value:{isCollapsed:t,setIsCollapsed:r},children:e.children})}function ll(e){const t=e.reduce((r,i)=>(r.set(i.context.spanId,{span:i,children:[]}),r),new Map),a=[];for(const r of e){const i=t.get(r.context.spanId);if(r.parentId===null||!t.has(r.parentId))a.push(i);else{const l=t.get(r.parentId);l&&l.children.push(i)}}for(const r of t.values())r.children.sort((i,l)=>new Date(i.span.startTime).valueOf()-new Date(l.span.startTime).valueOf());return a}const sn=30;function K1(e){const{spans:t,onSpanClick:a,selectedSpanNodeId:r}=e,i=ll(t);return n(il,{children:s("div",{css:m`
          display: flex;
          flex-direction: column;
          overflow: hidden;
          height: 100%;
          align-items: stretch;
        `,children:[n(ol,{}),n("ul",{css:m`
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
            width: 100%;
            overflow: auto;
          `,"data-testid":"trace-tree",children:i.map(l=>n(bt,{node:l,onSpanClick:a,selectedSpanNodeId:r},l.span.id))})]})})}function ol(){const e=be(i=>i.showMetricsInTraceTree),t=be(i=>i.setShowMetricsInTraceTree),{isCollapsed:a,setIsCollapsed:r}=vt();return n(R,{borderBottomWidth:"thin",borderColor:"dark",padding:"size-100",children:s(D,{direction:"row",justifyContent:"end",flex:"none",gap:"size-100",children:[s(A,{offset:5,children:[n(B,{variant:"default",size:"compact","aria-label":a?"Expand all":"Collapse all",onClick:()=>{r(!a)},icon:n(I,{svg:a?n(w.RowCollapseOutline,{}):n(w.RowExpandOutline,{})})}),n(Q,{children:a?"Expand all nested spans":"Collapse all nested spans"})]}),s(A,{offset:5,children:[n(B,{variant:"default",size:"compact","aria-label":e?"Hide metrics in trace tree":"Show metrics in trace tree",onClick:()=>{t(!e)},icon:n(I,{svg:e?n(w.TimerOutline,{}):n(w.TimerOffOutline,{})})}),n(Q,{children:e?"Hide metrics in trace tree":"Show metrics in trace tree"})]})]})})}const sl=m`
  font-weight: 500;
  color: var(--ac-global-text-color-900);
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;function bt(e){const{node:t,selectedSpanNodeId:a,onSpanClick:r,nestingLevel:i=0}=e,l=t.children,[o,d]=p.useState(!1),{isCollapsed:c}=vt(),u=l.length>0,h=be(x=>x.showMetricsInTraceTree);p.useEffect(()=>{d(c)},[c]);const{name:g,latencyMs:f,statusCode:L,tokenCountTotal:y,tokenCountPrompt:k,tokenCountCompletion:V}=t.span;return s("div",{children:[n("button",{className:"button--reset",css:m`
          width: 100%;
          min-width: 200px;
          cursor: pointer;
        `,onClick:()=>{p.startTransition(()=>{r&&r(t.span)})},children:s(cl,{isSelected:a===t.span.id,nestingLevel:i,children:[s(D,{direction:"row",gap:"size-100",justifyContent:"start",alignItems:"center",flex:"1 1 auto",minWidth:0,children:[n(rl,{spanKind:t.span.spanKind}),n("span",{css:sl,title:g,children:g}),L==="ERROR"?n(Ri,{statusCode:"ERROR"}):null,typeof y=="number"&&h?n(Oi,{tokenCountTotal:y,tokenCountPrompt:k??0,tokenCountCompletion:V??0}):null,f!=null&&h?n(Vi,{latencyMs:f,showIcon:!1}):null]}),n("div",{css:ml,"data-testid":"span-controls",children:u?n(gl,{isCollapsed:o,onClick:()=>{d(!o)}}):null})]})}),l.length?n("ul",{css:m`
            display: ${o?"none":"flex"};
            flex-direction: column;
          `,children:l.map((x,F)=>{const Y=l[F+1];return s("li",{css:m`
                  position: relative;
                `,children:[Y?n(dl,{...Y.span,nestingLevel:i}):null,n(ul,{...x.span,nestingLevel:i}),n(bt,{node:x,onSpanClick:r,selectedSpanNodeId:a,nestingLevel:i+1})]},x.span.context.spanId)})}):null]})}function cl(e){return n("div",{className:e.isSelected?"is-selected":"",css:m`
        width: 100%;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        gap: var(--ac-global-dimension-static-size-100);
        padding-right: var(--ac-global-dimension-static-size-100);
        padding-top: var(--ac-global-dimension-static-size-100);
        padding-bottom: var(--ac-global-dimension-static-size-100);
        border-left: 4px solid transparent;
        box-sizing: border-box;
        &:hover {
          background-color: var(--ac-global-color-grey-200);
        }
        &.is-selected {
          background-color: var(--ac-global-color-primary-300);
          border-color: var(--ac-global-color-primary);
        }
        & > *:first-child {
          margin-left: ${e.nestingLevel*sn+16}px;
        }
      `,children:e.children})}function dl({statusCode:e,nestingLevel:t}){return n("div",{"aria-hidden":"true","data-testid":"span-tree-edge-connector",css:a=>m`
        position: absolute;
        border-left: 1px solid
          ${e==="ERROR"?a.colors.statusDanger:"var(--ac-global-color-grey-700)"};
        top: 0;
        left: ${t*sn+29}px;
        width: 42px;
        bottom: 0;
        z-index: 1;
      `})}function ul({nestingLevel:e,statusCode:t}){return n("div",{"aria-hidden":"true",css:a=>{const r=t==="ERROR"?a.colors.statusDanger:"var(--ac-global-color-grey-700)";return m`
          position: absolute;
          border-left: 1px solid ${r};
          border-bottom: 1px solid ${r};
          border-radius: 0 0 0 11px;
          top: -5px;
          left: ${e*sn+29}px;
          width: 15px;
          height: 24px;
        `}})}const ml=m`
  width: 20px;
  flex: none;
`,pl=m`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--ac-global-text-color-900);
  border-radius: 4px;
  transition: transform 0.2s;
  transition: background-color 0.5s;
  flex: none;
  background-color: rgba(0, 0, 0, 0.1);
  &:hover {
    background-color: rgba(0, 0, 0, 0.3);
  }
  &.is-collapsed {
    transform: rotate(-90deg);
  }
`;function gl({isCollapsed:e,onClick:t}){return n("button",{onClick:a=>{a.stopPropagation(),a.preventDefault(),t()},className:On("button--reset",{"is-collapsed":e}),css:pl,children:n(I,{svg:n(w.ArrowIosDownwardOutline,{})})})}class z1 extends W.Component{constructor(t){super(t),this.state={hasError:!1,error:null}}static getDerivedStateFromError(t){return{hasError:!0,error:t}}componentDidCatch(t,a){}render(){return this.state.hasError?n(R,{padding:"size-200",children:s(D,{direction:"column",children:[s(D,{direction:"column",width:"100%",alignItems:"center",children:[n($n,{graphicKey:"error"}),n("h1",{children:"Something went wrong"})]}),n("p",{children:"We strive to do our very best but 🐛 bugs happen. It would mean a lot to us if you could file a an issue. If you feel comfortable, please include the error details below in your issue. We will get back to you as soon as we can."}),n(D,{direction:"row",width:"100%",justifyContent:"end",children:n(pe,{href:"https://github.com/Arize-ai/phoenix/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBUG%5D",children:"file an issue with us"})}),s("details",{open:!0,children:[n("summary",{children:"error details"}),n("pre",{css:m`
                  white-space: pre-wrap;
                  overflow-wrap: break-word;
                  overflow: hidden;
                  overflow-y: auto;
                  max-height: 500px;
                `,children:this.state.error instanceof Error?this.state.error.message:null})]})]})}):this.props.children}}const Ct=p.createContext(null);function kt(){let e=p.useContext(Ct);return e===null&&(console.warn("useMarkdownMode must be used within a MarkdownDisplayProvider"),e={mode:"text",setMode:()=>{}}),e}function $1(e){const t=be(i=>i.markdownDisplayMode),a=be(i=>i.setMarkdownDisplayMode),r=p.useCallback(i=>{p.startTransition(()=>{a(i)})},[a]);return n(Ct.Provider,{value:{mode:t,setMode:r},children:e.children})}const hl=m`
  a {
    color: var(--ac-global-color-primary);
    &:visited {
      color: var(--ac-global-color-purple-900);
    }
  }
`;function fl({children:e,mode:t}){return t==="markdown"?n("div",{css:hl,children:n(ia,{remarkPlugins:[la],children:e})}):n("pre",{css:m`
        white-space: pre-wrap;
        text-wrap: wrap;
        margin: 0;
      `,children:e})}function G1({children:e}){const{mode:t}=kt();return n(fl,{mode:t,children:e})}function Ll({mode:e,onModeChange:t}){return s(Re,{size:"compact",variant:"inline-button",value:e,onChange:a=>{t(a)},children:[n(H,{label:"text",value:"text",children:s(A,{placement:"top",delay:1e3,offset:10,children:[n(q,{children:n(I,{svg:n(va,{})})}),n(Q,{children:"Text"})]})}),n(H,{label:"markdown",value:"markdown",children:s(A,{placement:"top",delay:1e3,offset:10,children:[n(q,{children:n(I,{svg:n(ba,{})})}),n(Q,{children:"Markdown"})]})})]})}function B1(){const{mode:e,setMode:t}=kt();return n(Ll,{mode:e,onModeChange:t})}function Q1(e){const{spanKind:t}=e,a=p.useMemo(()=>{let r="grey-500";switch(t){case"llm":r="orange-1000";break;case"chain":r="blue-1000";break;case"retriever":r="seafoam-1000";break;case"reranker":r="celery-1000";break;case"embedding":r="indigo-1000";break;case"agent":r="grey-900";break;case"tool":r="yellow-1200";break;case"evaluator":r="indigo-1200";break;case"guardrail":r="fuchsia-1200";break}return r},[t]);return n(Xe,{color:a,children:t})}function yl(e){const{theme:t}=U(),a=t==="light"?void 0:en;return n(Ye,{value:e.value,extensions:[Gn(),Bn.lineWrapping,Qn(Un())],editable:!0,theme:a,...e})}const xt=m`
  .cm-content {
    padding: var(--ac-global-dimension-static-size-200) 0;
  }
  .cm-editor,
  .cm-gutters {
    background-color: transparent;
  }
`;function U1(e){const{theme:t}=U(),a=t==="light"?void 0:en;return n(Ye,{value:e.value,extensions:[Gn(),Bn.lineWrapping,Qn(Un())],editable:!1,theme:a,...e,basicSetup:{lineNumbers:!0,foldGutter:!0,bracketMatching:!0,syntaxHighlighting:!0,highlightActiveLine:!1,highlightActiveLineGutter:!1},css:xt})}function vl(e){const{theme:t}=U(),a=t==="light"?void 0:en;return n(Ye,{value:e.value,extensions:[Ma()],editable:!1,theme:a,...e,basicSetup:{lineNumbers:!1,foldGutter:!0,bracketMatching:!0,syntaxHighlighting:!0,highlightActiveLine:!1,highlightActiveLineGutter:!1},css:xt})}const bl=m`
  &.is-hovered {
    border: 1px solid var(--ac-global-input-field-border-color-active);
  }
  &.is-focused {
    border: 1px solid var(--ac-global-input-field-border-color-active);
  }
  &.is-invalid {
    border: 1px solid var(--ac-global-color-danger);
  }
  border-radius: ${zn.borderRadius.medium}px;
  border: 1px solid var(--ac-global-input-field-border-color);
  width: 100%;
  .cm-gutters,
  .cm-content,
  .cm-editor {
    border-radius: var(--ac-global-rounding-small);
  }
  .cm-focused {
    outline: none;
  }
  transition: all 0.2s ease-in-out;
`;function Cl({children:e,validationState:t,...a}){const[r,i]=p.useState(!1),[l,o]=p.useState(!1),d=t==="invalid";return n(Ca,{...a,validationState:d?"invalid":"valid",children:n("div",{className:On("json-editor-wrap",{"is-hovered":l,"is-focused":r,"is-invalid":d}),onFocus:()=>i(!0),onBlur:()=>i(!1),onMouseEnter:()=>o(!0),onMouseLeave:()=>o(!1),css:bl,children:e})})}function kl({str:e,excludePrimitives:t=!1,excludeArray:a=!1}){try{const r=JSON.parse(e);if(t&&typeof r!="object"||a&&Array.isArray(r))return!1}catch{return!1}return!0}function xl(e){return kl({str:e,excludeArray:!0,excludePrimitives:!0})}const wt=function(){var e={defaultValue:null,kind:"LocalArgument",name:"description"},t={defaultValue:null,kind:"LocalArgument",name:"metadata"},a={defaultValue:null,kind:"LocalArgument",name:"name"},r=[{alias:null,args:[{fields:[{kind:"Variable",name:"description",variableName:"description"},{kind:"Variable",name:"metadata",variableName:"metadata"},{kind:"Variable",name:"name",variableName:"name"}],kind:"ObjectValue",name:"input"}],concreteType:"DatasetMutationPayload",kind:"LinkedField",name:"createDataset",plural:!1,selections:[{alias:null,args:null,concreteType:"Dataset",kind:"LinkedField",name:"dataset",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"description",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"metadata",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"createdAt",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"exampleCount",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"experimentCount",storageKey:null}],storageKey:null}],storageKey:null}];return{fragment:{argumentDefinitions:[e,t,a],kind:"Fragment",metadata:null,name:"CreateDatasetFormMutation",selections:r,type:"Mutation",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[a,e,t],kind:"Operation",name:"CreateDatasetFormMutation",selections:r},params:{cacheID:"6aa615e27e1ccaa5431ba481842b43d0",id:null,metadata:{},name:"CreateDatasetFormMutation",operationKind:"mutation",text:`mutation CreateDatasetFormMutation(
  $name: String!
  $description: String = null
  $metadata: JSON = null
) {
  createDataset(input: {name: $name, description: $description, metadata: $metadata}) {
    dataset {
      id
      name
      description
      metadata
      createdAt
      exampleCount
      experimentCount
    }
  }
}
`}}}();wt.hash="5921369d33cc0fb1dffb5d943469a378";function St({datasetName:e,datasetDescription:t,datasetMetadata:a,onSubmit:r,isSubmitting:i,submitButtonText:l,formMode:o}){const{control:d,handleSubmit:c,formState:{isDirty:u}}=Ne({defaultValues:{name:e??"Dataset "+new Date().toISOString(),description:t??"",metadata:JSON.stringify(a,null,2)??"{}"}});return s(we,{children:[s(R,{padding:"size-200",children:[n(N,{name:"name",control:d,rules:{required:"Dataset name is required"},render:({field:{onChange:h,onBlur:g,value:f},fieldState:{invalid:L,error:y}})=>n($,{label:"Dataset Name",description:"The name of the dataset",errorMessage:y==null?void 0:y.message,validationState:L?"invalid":"valid",onChange:h,onBlur:g,value:f.toString()})}),n(N,{name:"description",control:d,render:({field:{onChange:h,onBlur:g,value:f},fieldState:{invalid:L,error:y}})=>n(ka,{label:"description",description:"A description of the dataset",isRequired:!1,height:100,errorMessage:y==null?void 0:y.message,validationState:L?"invalid":"valid",onChange:h,onBlur:g,value:f==null?void 0:f.toString()})}),n(N,{name:"metadata",control:d,rules:{validate:h=>xl(h)?!0:"metadata must be a valid JSON object"},render:({field:{onChange:h,onBlur:g,value:f},fieldState:{invalid:L,error:y}})=>n(Cl,{validationState:L?"invalid":"valid",label:"metadata",errorMessage:y==null?void 0:y.message,description:"A JSON object containing metadata for the dataset",children:n(yl,{value:f,onChange:h,onBlur:g})})})]}),n(R,{paddingEnd:"size-200",paddingTop:"size-100",paddingBottom:"size-100",borderTopColor:"light",borderTopWidth:"thin",children:n(D,{direction:"row",justifyContent:"end",children:n(B,{disabled:o==="edit"?!u:!1,variant:u?"primary":"default",size:"compact",loading:i,onClick:c(r),children:l})})})]})}function H1(e){const{onDatasetCreated:t,onDatasetCreateError:a}=e,[r,i]=Z.useMutation(wt),l=p.useCallback(o=>{r({variables:{...o,metadata:JSON.parse(o.metadata)},onCompleted:d=>{t(d.createDataset.dataset)},onError:d=>{a(d)}})},[r,t,a]);return n(St,{isSubmitting:i,onSubmit:l,submitButtonText:i?"Creating...":"Create Dataset",formMode:"create"})}function Fn(e){const t=Date.now(),a=Le(De(t,365));switch(e){case"1d":return{start:Le(ae(t,1)),end:a};case"7d":return{start:Le(ae(t,7)),end:a};case"30d":return{start:Le(ae(t,30)),end:a};case"all":return{start:new Date("01/01/1971"),end:a};default:P()}}const Mt=p.createContext(null);function wl(){const e=W.useContext(Mt);if(e===null)throw new Error("useLastNTimeRange must be used within a LastNTimeRangeProvider");return e}function Z1({initialTimeRangeKey:e="7d",children:t}){const[a,r]=p.useState(e),[i,l]=p.useState(()=>Fn(e)),o=p.useCallback(d=>{p.startTransition(()=>{r(d),l(Fn(d))})},[]);return n(Mt.Provider,{value:{timeRangeKey:a,setTimeRangeKey:o,timeRange:i},children:t})}const Tt=[{key:"1d",label:"Last Day"},{key:"7d",label:"Last 7 Days"},{key:"30d",label:"Last Month"},{key:"all",label:"All Time"}];Tt.reduce((e,t)=>({...e,[t.key]:t}),{});function Sl(e){const{isDisabled:t,selectedKey:a,onSelectionChange:r}=e;return n(xe,{"aria-label":"Time Range",addonBefore:n(I,{svg:n(w.CalendarOutline,{})}),isDisabled:t,defaultSelectedKey:a,onSelectionChange:i=>{r&&r(i)},align:"end",children:Tt.map(({key:i,label:l})=>n(_,{children:l},i))})}function j1(){const{timeRangeKey:e,setTimeRangeKey:t}=wl();return n(Sl,{selectedKey:e,onSelectionChange:t})}function q1({indeterminate:e,...t}){const a=p.useRef(null);return W.useEffect(()=>{typeof e=="boolean"&&(a.current.indeterminate=!t.checked&&e)},[a,e,t.checked]),n("div",{onClick:r=>{r.stopPropagation()},children:n("input",{type:"checkbox",ref:a,css:m`
          cursor: pointer;
        `,...t})})}function W1({getValue:e}){const t=e();if(!Ia(t))throw new Error("TimestampCell only supports number or null values.");const a=t!=null?new Date(t).toLocaleString([],{year:"numeric",month:"numeric",day:"numeric",hour:"2-digit",minute:"2-digit"}):"--";return n("time",{title:t!=null?String(t):"",children:a})}function J1(e){return n("button",{className:"button--reset",onClick:t=>{t.stopPropagation(),e.onClick(t)},"aria-label":e["aria-label"],css:m`
        color: var(--ac-global-text-color-white-900);
        .ac-icon-wrap {
          font-size: 1.2rem;
        }

        &:hover {
          color: var(--ac-global-color-primary);
        }
      `,children:n(I,{svg:e.isExpanded?n(w.ChevronDownOutline,{}):n(w.ChevronRightOutline,{})})})}function Ml(e){const{size:t=28}=e;return s("svg",{xmlns:"http://www.w3.org/2000/svg",xmlnsXlink:"http://www.w3.org/1999/xlink",viewBox:"0 0 305.92 350.13",width:t,height:t,css:m`
        .cls-1 {
          fill: url(#linear-gradient);
        }

        .cls-2 {
          fill: url(#Fade_to_Black_2-2);
        }

        .cls-2,
        .cls-3 {
          opacity: 0.5;
        }

        .cls-4 {
          fill: #fedbb5;
        }

        .cls-5 {
          fill: #e5b4a6;
        }

        .cls-6 {
          fill: url(#Fade_to_Black_2);
        }

        .cls-6,
        .cls-7,
        .cls-8,
        .cls-9,
        .cls-10,
        .cls-11,
        .cls-12,
        .cls-13,
        .cls-14 {
          opacity: 0.4;
        }

        .cls-3 {
          fill: url(#linear-gradient-10);
        }

        .cls-7 {
          fill: url(#linear-gradient-6);
        }

        .cls-8 {
          fill: url(#linear-gradient-3);
        }

        .cls-9 {
          fill: url(#linear-gradient-4);
        }

        .cls-10 {
          fill: url(#linear-gradient-2);
        }

        .cls-11 {
          fill: url(#linear-gradient-7);
        }

        .cls-12 {
          fill: url(#linear-gradient-5);
        }

        .cls-13 {
          fill: url(#linear-gradient-8);
        }

        .cls-14 {
          fill: url(#linear-gradient-9);
        }
      `,children:[s("defs",{children:[s("linearGradient",{id:"linear-gradient",x1:"45.77",y1:"21.43",x2:"201.89",y2:"291.83",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#18bab6"}),n("stop",{offset:".5",stopColor:"#00adee"}),n("stop",{offset:"1",stopColor:"#0095c4"})]}),s("linearGradient",{id:"linear-gradient-2",x1:"197.65",y1:"237.84",x2:"65.97",y2:"9.77",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#fdfdfe",stopOpacity:"0"}),n("stop",{offset:".11",stopColor:"#fdfdfe",stopOpacity:".17"}),n("stop",{offset:".3",stopColor:"#fdfdfe",stopOpacity:".42"}),n("stop",{offset:".47",stopColor:"#fdfdfe",stopOpacity:".63"}),n("stop",{offset:".64",stopColor:"#fdfdfe",stopOpacity:".79"}),n("stop",{offset:".78",stopColor:"#fdfdfe",stopOpacity:".9"}),n("stop",{offset:".91",stopColor:"#fdfdfe",stopOpacity:".97"}),n("stop",{offset:"1",stopColor:"#fdfdfe"})]}),n("linearGradient",{id:"linear-gradient-3",x1:"158.8",y1:"236.43",x2:"63.93",y2:"72.09",xlinkHref:"#linear-gradient-2"}),n("linearGradient",{id:"linear-gradient-4",x1:"145.73",y1:"248.43",x2:"92.77",y2:"156.7",xlinkHref:"#linear-gradient-2"}),n("linearGradient",{id:"linear-gradient-5",x1:"147.93",y1:"266.95",x2:"114.95",y2:"209.83",xlinkHref:"#linear-gradient-2"}),s("linearGradient",{id:"linear-gradient-6",x1:"92.25",y1:"261.75",x2:"92.25",y2:"321.91",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#231f20"}),n("stop",{offset:".03",stopColor:"#231f20",stopOpacity:".9"}),n("stop",{offset:".22",stopColor:"#231f20",stopOpacity:".4"}),n("stop",{offset:".42",stopColor:"#231f20",stopOpacity:".1"}),n("stop",{offset:".65",stopColor:"#231f20",stopOpacity:"0"})]}),s("linearGradient",{id:"Fade_to_Black_2","data-name":"Fade to Black 2",x1:"159.88",y1:"256.07",x2:"159.88",y2:"286.75",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#231f20"}),n("stop",{offset:"1",stopColor:"#231f20",stopOpacity:"0"})]}),s("linearGradient",{id:"linear-gradient-7",x1:"174.69",y1:"176.58",x2:"174.69",y2:"151.5",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#231f20"}),n("stop",{offset:".03",stopColor:"#231f20",stopOpacity:".95"}),n("stop",{offset:".51",stopColor:"#231f20",stopOpacity:".26"}),n("stop",{offset:".81",stopColor:"#231f20",stopOpacity:"0"})]}),s("linearGradient",{id:"linear-gradient-8",x1:"229.53",y1:"195.1",x2:"229.53",y2:"134.41",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#231f20"}),n("stop",{offset:".18",stopColor:"#231f20",stopOpacity:".48"}),n("stop",{offset:".38",stopColor:"#231f20",stopOpacity:".12"}),n("stop",{offset:".58",stopColor:"#231f20",stopOpacity:"0"})]}),n("linearGradient",{id:"Fade_to_Black_2-2","data-name":"Fade to Black 2",x1:"286",y1:"242.89",x2:"265.05",y2:"206.61",xlinkHref:"#Fade_to_Black_2"}),n("linearGradient",{id:"linear-gradient-9",x1:"302.87",y1:"232.93",x2:"271.49",y2:"178.58",xlinkHref:"#linear-gradient-2"}),s("linearGradient",{id:"linear-gradient-10",x1:"221.39",y1:"223.73",x2:"267.07",y2:"197.36",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#231f20"}),n("stop",{offset:".31",stopColor:"#231f20",stopOpacity:".5"}),n("stop",{offset:".67",stopColor:"#231f20",stopOpacity:".13"}),n("stop",{offset:"1",stopColor:"#231f20",stopOpacity:"0"})]})]}),s("g",{id:"Layer_1-2","data-name":"Layer 1",children:[n("path",{className:"cls-1",d:"m305.42,218.76c-.9-4.06-2.96-7.8-6.14-11.13-1.22-1.28-2.59-2.48-4.07-3.58-.72-.53-1.48-1.03-2.26-1.52-.97-.6-1.98-1.19-3.07-1.75-4.05-2.08-7.5-4.17-10.53-6.41-1.23-.91-2.42-1.86-3.53-2.83-2.71-2.37-4.53-4.38-5.88-6.53-.44-.69-.83-1.44-1.2-2.14-.16-.31-.39-.57-.66-.77-.49-.36-1.12-.52-1.75-.4-.97.18-1.72.97-1.83,1.96-.09.76-.08,1.57.02,2.41.06.5-.2.96-.66,1.17-.11.05-.22.08-.33.09-.64.08-1.23.43-1.6.96-.37.54-.48,1.2-.33,1.83.14.55.32.93.48,1.24l.14.28c.1.19.2.39.31.58.3.57.62,1.15,1,1.71.71,1.04,1.52,2.07,2.46,3.18.3.35.35.86.13,1.27-.22.41-.68.64-1.14.58-5.37-.73-10.17-1.93-14.65-3.59-.51-.19-1.03-.37-1.53-.57-4.02-1.69,3.23-8.92,6.55-14.03,14.55-22.37,17.56-48,17.68-73.93.12-25.07-2.59-49.78-7.57-74.18v-.04c-3.25-20.44-6.01-28.12-7.74-30.97-.37-.76-.78-1.22-1.21-1.45-.48-.32-.73-.17-.73-.17-.93.03-2.01.87-3.3,2.22-5.42,5.71-5.12,12.49-3.62,19.58,6.85,32.22,12.01,64.63,9.66,97.75-1.61,22.83-5.87,44.82-21.82,62.69-.96,1.08-1.99,2.08-3.02,3.1-1.2,1.17-3.04,3.46-4.42,2.51-1.84-1.28-.2-3.9.37-5.25,9.35-21.89,12.04-44.77,10.6-68.36-.03-.55-.09-1.09-.13-1.63l.02-.03c-.04-.44-.08-.85-.12-1.28-.24-3.12-.53-6.23-.92-9.33-4.02-37.42-8.84-39.84-8.84-39.84h0c-.32-.28-.72-.51-1.25-.62-2.53-.53-3.92,1.7-5.04,3.39-5.07,7.6-2.83,15.67-1.19,23.67,5.73,28.01,5.82,55.75-4.02,83-.9,2.48-1.98,4.9-3.12,7.28-1.2,2.53-1.99,5.7-6.12,4.34-3.86-1.28-2.78-4.2-2.27-6.87,1.29-6.79,2.33-13.59,2.98-20.42l.02.04c.06-.67.1-1.32.16-1.98.1-1.18.17-2.36.24-3.54.06-.99.11-1.96.15-2.91.02-.49.04-.97.06-1.46.78-21.63-2.85-31.46-4.23-34.37-.15-.36-.32-.68-.51-.97h0s0,0,0,0c-1.43-2.14-3.8-1.89-5.84.13-3.76,3.72-5.84,8.1-4.88,13.62,2.8,16.09,1.16,32.03-1.84,47.9-.41,2.13-1.36,6-5.9,5.01-3.09-.68-3.81-2.01-3.99-4.69.03-2.03.01-4.05-.06-6.08,0-.05,0-.1,0-.15h0c-.01-.29-.03-.57-.04-.86v-.02c0-.14,0-.27-.02-.4-.13-2.76-.36-5.53-.7-8.3-.03-.27-.08-.53-.12-.79-1.74-15.62-4-17.13-4-17.13-1.45-1.88-3.71-1.57-5.67.38-3.76,3.72-5.67,8.08-4.88,13.62.57,4.06.43,2.81.84,6.34.33,1.82.66,5.13.69,6.19-.09.94-.32,1.76-.9,2.37-1.92,2.07-5.02-.05-7.37-1.02-45.52-18.84-84.49-45.28-118.5-78.71C29.51,74.47,6.74,46.89,6.74,46.89h0c-.84-.99-1.91-1.55-3.53-.85C.24,47.32.33,51.13.06,54.33c-.54,6.41,2.88,11.07,6.62,15.42,51.36,59.92,114.05,102.98,189.7,124.51l13.61,3.61c.16.04.32.08.48.12.03,0,.05.02.07.02l11.72,3.11.32.08c-.38.11-.82.2-1.28.28-12.9,2.55-38.42-2.14-58.91-6.92-10.15-2.13-20.1-4.71-29.85-7.79-.45-.13-.69-.2-.69-.2v-.02c-37.88-12.05-72.58-31.59-102.92-61.4-2.87-2.82-5.54-5.86-8.15-8.95-2.41-2.86-7.36-8.84-9.06-10.89-.19-.27-.39-.51-.6-.73h0s0,0,0,0c-.52-.53-1.14-.87-2.03-.66-2.12.49-2.72,2.67-3.11,4.51-1.55,7.39.8,13.59,5.76,19.15,31.09,34.84,70.09,57.1,113.9,71.7,24.88,8.29,50.46,13.32,76.57,16.54-15.56,5.04-31.58,6.57-47.72,6.17-31.26-.78-60.57-8.29-88.12-21.68-10.16-5.22-19.62-11.05-22.11-12.6-1.43-.98-2.9-1.57-4.36-.45-2.74,2.12-.85,5.85.03,8.76,1.69,5.6,5.58,9.47,10.63,12.14,44.88,23.74,92.26,33.22,142.71,24.8,5.11-.85,9.95-1.79,15.29-3.59-8.43,7.3-18.2,12.06-28.47,15.82-31.59,11.56-62.98,11.09-94.25,3.27-10.03-2.69-21.68-7.05-21.68-7.05h0c-1.68-.73-3.34-.99-4.64.87-2.28,3.27-.29,6.66,1.68,9.74,4.67,7.27,13.68,7.98,20.81,10.44,2.44.77-4.2,5.21-6.34,6.84-10.34,7.91-20.46,15.14-30.76,22.8l-6.74,4.97h0c-1.16.8-2.18,1.69-1.64,3.37.61,1.88,2.57,2.22,4.47,2.62,7.37,1.53,13.66-.92,19.48-5.27,12.48-9.35,25.18-18.41,37.39-28.11,4.64-3.7,8.86-3.39,15.21-1.74-15.88,11.97-30.73,23.17-45.6,34.36-15.08,11.35-30.18,22.7-45.28,34.03l-9.98,7.38c-.15.1-.29.21-.43.32l-.15.11h0c-.85.68-1.48,1.44-1.3,2.44.4,2.25,3.05,2.81,5.21,3.18,8.92,1.54,14.44-1.82,20.54-6.39,30.5-22.9,61.12-45.64,91.44-68.76,6.8-5.18,13.79-8.11,23.61-7.01-8.36,6.25-16.38,12.24-24.3,18.16l-21.51,15.92c-.15.11-.3.22-.45.33h-.02c-1.14.9-1.94,1.96-1.49,3.53.82,2.84,4.24,3.18,7.15,3.62,5.34.8,9.87-1.09,14.06-4.21,2.41-1.8,4.84-3.57,7.28-5.33h0s32.84-26.08,32.84-26.08c0,0,7.76-5.54,16.74-10.64.8-.5,1.61-1,2.41-1.49.34-.15,1.2-.54,2.48-1.16.97-.5,1.93-.99,2.89-1.44,1.41-.72,3.05-1.59,4.88-2.59,5.3-2.2,20.44-9.27,32.98-22.62,5.96-4.6,14.34-10.6,20.87-13.49h0s.04-.02.04-.02c.5-.22.98-.42,1.46-.6h0s.03,0,.06-.02c.32-.12.63-.23.93-.33l.84-.33c2.36-.67,6.22-.92,6.71,4.29.09,1.28.06,2.59-.08,3.97-.11,1.04-.3,2.14-.46,3.02-.15.85.2,1.71.88,2.21.11.08.22.15.34.21.9.44,1.99.24,2.66-.51.25-.28.51-.55.77-.83,3.22-3.38,6.47-5.73,9.95-7.16,5.07-2.1,10.2-2.11,15.68-.02,2.6.99,5.05,2.34,7.48,4.14,1.03.76,2.08,1.62,3.11,2.55.61.56,1.22,1.18,1.76,1.72l.09.09.44.45c.08.08.17.16.26.22.52.38,1.18.53,1.82.39.75-.16,1.37-.69,1.63-1.41.05-.14.1-.28.15-.41,1.56-4.59,1.87-8.82.97-12.93Z"}),n("path",{className:"cls-4",d:"m208.42,169.5c-.37,2.28-.76,4.55-1.19,6.82.43-2.27.82-4.55,1.19-6.82h0Z"}),n("path",{className:"cls-4",d:"m248.79,194.81c.16.07.33.13.5.19-.17-.06-.33-.13-.5-.19"}),n("path",{className:"cls-4",d:"m230.37,180.81s0,0,0,.01c0,0,0,0,0-.01"}),n("path",{className:"cls-4",d:"m230.5,180.5s-.03.06-.04.1c.01-.03.03-.07.04-.1"}),n("path",{className:"cls-4",d:"m255.55,180.46s-.05.08-.08.13c.03-.04.05-.08.08-.13"}),n("path",{className:"cls-4",d:"m215.62,178.85c-.28.59-.54,1.22-.82,1.82.28-.59.54-1.22.82-1.82"}),n("path",{className:"cls-4",d:"m188.53,177.51s.01,0,.02,0c0,0-.01,0-.02,0"}),n("polyline",{className:"cls-4",points:"184.47 175.68 184.47 175.69 184.47 175.68"}),n("polyline",{className:"cls-4",points:"184.45 175.66 184.46 175.66 184.45 175.66"}),n("polyline",{className:"cls-4",points:"184.43 175.62 184.44 175.64 184.43 175.62"}),n("path",{className:"cls-4",d:"m184.42,175.6s0,0,0,.01c0,0,0,0,0-.01"}),n("path",{className:"cls-4",d:"m184.39,175.57s.01.02.02.03c0-.01-.01-.02-.02-.03"}),n("path",{className:"cls-4",d:"m183.65,172.72s0,.01,0,.02c0,0,0-.01,0-.02"}),n("path",{className:"cls-4",d:"m193.79,171c-.08.46-.17.91-.26,1.37.09-.46.17-.91.26-1.37"}),n("path",{className:"cls-4",d:"m168.79,167.86c-.3.32-.63.54-.99.68.35-.14.68-.36.99-.68"}),n("path",{className:"cls-5",d:"m184.47,175.69c.25.35.57.64.99.9h0c-.42-.25-.74-.55-.99-.9m-.02-.03s0,.01.01.02c0,0,0-.01-.01-.02m-.02-.02v.02s0-.01,0-.02m-.01-.02s0,0,0,0c0,0,0,0,0,0m-.01-.01s0,0,0,0c0,0,0,0,0,0m-.02-.04s0,0,0,0c0,0,0,0,0,0m-.74-2.82s0,.01,0,.01c0,0,0,0,0-.01m0-.06h0s0,.03,0,.04c0-.01,0-.02,0-.04m-19.74-4.71s.03.01.04.02c.95.41,1.9.74,2.79.74.37,0,.73-.06,1.06-.19-.34.13-.69.19-1.06.19-.9,0-1.87-.34-2.83-.75m19.61-2.97s0,.01,0,.02c0,0,0-.01,0-.02"}),n("path",{className:"cls-5",d:"m249.29,195c.08.03.16.06.24.09h0c-.08-.03-.16-.06-.24-.09m-18.14-7.32s0,0-.01,0c0,0,.01,0,.01,0m-2.75-1.47c0,.64.22,1.23.85,1.66.23.16.47.23.71.23.38,0,.77-.16,1.17-.41-.4.25-.79.41-1.17.41-.25,0-.49-.07-.72-.23-.63-.43-.85-1.02-.85-1.66m1.33-3.84c-.04.08-.07.17-.11.25.04-.08.07-.17.11-.25m.64-1.54c-.21.51-.42,1.02-.64,1.53.22-.51.43-1.02.64-1.53m.09-.23c-.03.07-.06.14-.09.22.03-.07.06-.14.09-.22m25.01-.01s-.01.02-.02.03c0-.01.01-.02.02-.03m.1-.16s-.01.02-.02.03c0-.01.01-.02.02-.03m-25.03-.01s-.03.06-.04.09c.01-.03.02-.06.04-.09m-23.84-.69c0,1.46.59,2.74,2.81,3.47.68.23,1.28.33,1.8.33,1.87,0,2.77-1.32,3.5-2.85-.73,1.53-1.62,2.85-3.5,2.85-.52,0-1.11-.1-1.8-.33-2.22-.73-2.8-2.01-2.81-3.47m-18.18-2.21h.01-.01m3.63-1.49c-.67.87-1.65,1.51-3.14,1.51-.15,0-.3,0-.46-.02.16.01.31.02.46.02,1.48,0,2.47-.63,3.14-1.51m28.75-10.95s-.01,0-.02,0c-.66,2.17-1.35,4.33-2.13,6.49-.9,2.48-1.98,4.9-3.12,7.28h0c1.13-2.38,2.22-4.8,3.12-7.28.78-2.16,1.5-4.33,2.16-6.49m-25.9-1.2c-.36,2.38-.76,4.75-1.2,7.12.44-2.37.84-4.75,1.2-7.12h0m58.07-11.39s0,0,0,0c-3.26,10.69-8.32,20.76-16.37,29.77-.96,1.08-1.99,2.08-3.02,3.1h0c1.03-1.01,2.06-2.02,3.02-3.1,8.05-9.02,13.12-19.09,16.38-29.78"}),n("path",{className:"cls-10",d:"m4.56,45.73c-.4,0-.85.09-1.34.31-2.11.91-2.68,3.11-2.93,5.45,11.33,14.85,56.07,69.62,126.46,107.18,0,0,68.91,36.38,138.24,40.31-5.37-.73-10.17-1.93-14.65-3.59-.26-.1-.53-.19-.8-.29h0c-25.19-5.44-46.66-12.25-61.84-17.7.29.06.57.1.84.13-.28-.03-.57-.07-.88-.14-.92-.2-1.62-.46-2.17-.79-12.01-4.39-19.66-7.76-21.51-8.59-.88-.38-1.75-.83-2.53-1.15-45.52-18.84-84.49-45.28-118.5-78.71C29.51,74.47,6.74,46.89,6.74,46.89h0c-.58-.68-1.28-1.16-2.18-1.16"}),n("path",{className:"cls-8",d:"m9.57,103.87c-.16,0-.33.02-.51.06-2.12.49-2.72,2.67-3.11,4.51-.07.33-.13.66-.18.99,35.19,47.67,82.41,67.15,82.41,67.15,47.15,22.21,85.84,26.69,109.4,26.69,9.75,0,16.91-.77,21.01-1.37-1.87.21-3.93.31-6.14.31-13.81,0-33.56-3.79-50.06-7.64-10.15-2.13-20.1-4.71-29.85-7.79-.45-.13-.69-.2-.69-.2v-.02c-37.88-12.05-72.58-31.59-102.92-61.4-2.87-2.82-5.54-5.86-8.15-8.95-2.41-2.86-7.36-8.84-9.06-10.89-.19-.27-.39-.51-.6-.73h0s0,0,0,0c-.41-.42-.9-.72-1.53-.72"}),n("path",{className:"cls-9",d:"m41.57,186.66c-.56,0-1.13.18-1.69.61-2.39,1.85-1.26,4.91-.35,7.6,17.64,10.71,58.1,31.53,106.02,31.53,18.09,0,37.24-2.97,56.64-10.57-14,4.54-28.37,6.23-42.87,6.23-1.61,0-3.23-.02-4.85-.06-31.26-.78-60.57-8.29-88.12-21.68-10.16-5.22-19.62-11.05-22.11-12.6-.88-.6-1.78-1.06-2.68-1.06"}),n("path",{className:"cls-12",d:"m205.41,231.93c-7.68,5.89-16.32,9.97-25.34,13.27-16.95,6.2-33.84,8.94-50.68,8.94-14.56,0-29.08-2.05-43.57-5.67-10.03-2.69-21.68-7.05-21.68-7.05h0c-.74-.32-1.47-.55-2.17-.55-.9,0-1.74.38-2.47,1.42-1.06,1.52-1.2,3.07-.85,4.6,11.13,5.17,35,14.36,64.11,14.36,25.24,0,54.41-6.9,82.66-29.31"}),n("path",{className:"cls-7",d:"m130.35,268.02c-27.34,0-48.01-5.54-50.62-6.27.77.23,1.52.46,2.26.71,2.44.77-4.2,5.21-6.34,6.84-7.65,5.85-15.17,11.32-22.73,16.88h23.2c7.31-5.4,14.6-10.84,21.72-16.5,2.65-2.11,5.15-2.91,7.99-2.91,2.15,0,4.48.46,7.22,1.17-15.88,11.97-30.73,23.17-45.6,34.36-8.69,6.54-17.39,13.07-26.09,19.61h23.34c20.99-15.71,41.97-31.42,62.82-47.32,4.81-3.67,9.71-6.2,15.64-6.98-4.39.29-8.67.41-12.8.41Z"}),n("path",{className:"cls-6",d:"m125.47,286.75h22.55l16.66-13.24s7.76-5.54,16.74-10.64c.8-.5,1.61-1,2.41-1.49.34-.15,1.2-.54,2.48-1.16.97-.5,1.93-.99,2.89-1.44,1.46-.75,3.18-1.65,5.09-2.71-16.08,6.73-32.54,10.02-47.79,11.29.21,0,.42,0,.63,0,1.28,0,2.61.07,3.99.23-8.36,6.25-16.38,12.24-24.3,18.16l-1.36,1Z"}),n("path",{className:"cls-11",d:"m183.65,172.69c.03-2.03.01-4.05-.06-6.08v-.15s0,0,0,0c-.01-.29-.03-.57-.04-.86v-.02s-.02-.4-.02-.4c-.08-1.7-.21-3.41-.37-5.12-5.38-2.26-10.45-5.15-15.12-8.56.03.48.05.96.12,1.46.57,4.06.43,2.81.84,6.34.33,1.82.66,5.13.69,6.19-.09.94-.32,1.76-.9,2.37-.59.63-1.29.87-2.05.87-.9,0-1.87-.34-2.83-.75,1.78.8,9.45,4.19,21.55,8.61-1.3-.79-1.69-2.01-1.81-3.9Z"}),n("path",{className:"cls-13",d:"m271.38,134.41c-5.03,7.01-11.24,13.15-18.32,18.08-3.26,10.69-8.32,20.76-16.37,29.77-.96,1.08-1.99,2.08-3.02,3.1-1,.97-2.45,2.73-3.7,2.73-.25,0-.49-.07-.72-.23-1.84-1.28-.2-3.9.37-5.25,3.02-7.06,5.33-14.23,7.04-21.49-5.04,1.89-10.33,3.22-15.79,3.96-.66,2.17-1.35,4.33-2.13,6.49-.9,2.48-1.98,4.9-3.12,7.28-1,2.11-1.72,4.67-4.32,4.67-.52,0-1.11-.1-1.8-.33-3.86-1.28-2.78-4.2-2.27-6.87.67-3.54,1.27-7.08,1.79-10.63-4.8-.15-9.49-.77-14.03-1.82-.43,2.83-.92,5.67-1.46,8.49-.36,1.89-1.16,5.17-4.53,5.17-.4,0-.85-.05-1.33-.15,15.19,5.45,36.66,12.26,61.84,17.71h0c-.25-.1-.5-.19-.74-.29-4.02-1.69,3.23-8.92,6.55-14.03,9.35-14.37,13.92-30.09,16.03-46.36Z"}),n("path",{className:"cls-2",d:"m267.61,212.35c-3.15,0-6.32.3-9.44.88-.59.11-1.17.16-1.72.16-.89,0-1.72-.13-2.5-.37.13.16.25.3.37.47,1.37,1.9,2.08,3.98,2.35,6.14.34.37.63.84.86,1.43h0s0,.02.01.03c0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,0,0,.01,0,0,0,0,0,.01,0,0,0,.01,0,.01,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,0,0,0v.02s0,0,0,.01c0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.02,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,.01,0,.02,0,.03,0,0,0,0,0,0,0,0,0,0,0,.01t0,0s0,.02,0,.03c0,0,0,0,0,0,0,0,0,.02,0,.03,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,0,0,.02,0,0,0,.01,0,.02,0,0,0,.01,0,.01,0,0,0,.01,0,.01,0,0,0,.01,0,.02,0,0,0,.01,0,.01,0,0,0,0,0,.02s0,.01,0,.02c0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,.01,0,.01s0,.01,0,.01c0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.02,0,.03,0,0,0,0,0,0,0,0,0,.02,0,.03,0,0,0,0,0,0,0,0,0,.02,0,.02,0,0,0,0,0,0,0,.01,0,.02,0,.03,0,0,0,0,0,0,0,0,0,.02,0,.03,0,0,0,0,0,0,0,0,0,.02,0,.03h0s0,.03,0,.04h0s0,.02,0,.03h0s0,.03,0,.03h0s0,.03,0,.04h0s0,.02,0,.03h0s0,.02,0,.03h0s0,.02,0,.03h0s0,.02,0,.04c0,0,0,0,0,0,0,.03.01.07.01.1h0s0,.03,0,.04h0s0,.07.01.11h0s0,.02,0,.04h0s0,.03,0,.04h0s0,.05,0,.07h0s0,.02,0,.04h0s0,.03,0,.04h0s0,.03,0,.04h0c.03.5.05,1,.05,1.52,0,.8-.04,1.61-.13,2.46-.11,1.04-.3,2.14-.46,3.02-.02.13-.04.27-.04.4,0,.71.34,1.39.92,1.81l.34.21c.32.16.66.23,1,.23.62,0,1.23-.26,1.67-.74.25-.28.51-.55.77-.83,3.22-3.38,6.47-5.73,9.95-7.16,2.54-1.05,5.1-1.58,7.71-1.58s5.24.52,7.96,1.56c2.6.99,5.05,2.34,7.48,4.14,1.03.76,2.08,1.62,3.11,2.55.61.56,1.22,1.18,1.76,1.72l.09.09.44.45.26.22c.38.28.83.43,1.3.44-2.15-4.61-4.88-8.9-8.73-12.24-7.28-6.31-16.46-8.98-25.8-8.98"}),n("path",{className:"cls-14",d:"m266.74,181.67l-.41.04c-.97.18-1.72.97-1.83,1.96-.09.76-.08,1.57.02,2.41.03.26-.03.52-.16.73,3.89,5.78,12.33,16.03,25.15,19.91,0,0,19.81,10.36,14.8,25.38h0l.15-.41c1.56-4.59,1.87-8.82.97-12.93-.9-4.06-2.96-7.8-6.14-11.13-1.22-1.28-2.59-2.48-4.07-3.58-.72-.53-1.48-1.03-2.26-1.52-.97-.6-1.98-1.19-3.07-1.75-4.05-2.08-7.5-4.17-10.53-6.41-1.23-.91-2.42-1.86-3.53-2.83-2.71-2.37-4.53-4.38-5.88-6.53-.44-.69-.83-1.44-1.2-2.14-.16-.31-.39-.57-.66-.77-.38-.28-.85-.44-1.34-.44"}),n("path",{className:"cls-3",d:"m241.61,223.53l4.01-2.33,16.87-22.61s-9.24-1.75-13.7-3.78c0,0-4.64,21.12-21.73,38.76l6.3-4.67c2.51-1.76,4.79-3.29,8.24-5.37Z"})]})]})}const Tl=m`
  padding: var(--px-spacing-med) var(--px-spacing-med) var(--px-spacing-med)
    12px;
  border-bottom: 1px solid var(--ac-global-color-grey-200);
  flex: none;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`,Il=m`
  padding: var(--px-spacing-lg) var(--px-spacing-med);
  flex: none;
  display: flex;
  flex-direction: column;
  background-color: var(--ac-global-color-grey-75);
  border-right: 1px solid var(--ac-global-color-grey-200);
  box-sizing: border-box;
  height: 100vh;
  position: fixed;
  width: var(--px-nav-collapsed-width);
  z-index: 2; // Above the content
  transition:
    width 0.15s cubic-bezier(0, 0.57, 0.21, 0.99),
    box-shadow 0.15s cubic-bezier(0, 0.57, 0.21, 0.99);
  &[data-expanded="true"] {
    width: var(--px-nav-expanded-width);
    box-shadow: 0 0 30px 0 rgba(0, 0, 0, 0.2);
  }
`,cn=m`
  width: 100%;
  color: var(--ac-global-color-grey-500);
  background-color: transparent;
  border-radius: var(--ac-global-rounding-small);
  display: flex;
  flex-direction: row;
  align-items: center;
  overflow: hidden;
  transition:
    color 0.2s ease-in-out,
    background-color 0.2s ease-in-out;
  text-decoration: none;
  &.active {
    color: var(--ac-global-color-grey-1200);
    background-color: var(--ac-global-color-primary-300);
  }
  &:hover:not(.active) {
    color: var(--ac-global-color-grey-1200);
    background-color: var(--ac-global-color-grey-200);
  }
  & > .ac-icon-wrap {
    padding: var(--ac-global-dimension-size-50);
    display: inline-block;
  }
`,Dl=e=>m`
  color: var(--ac-global-text-color-900);
  font-size: ${e.typography.sizes.large.fontSize}px;
  text-decoration: none;
  margin: 0 0 var(--px-spacing-lg) 0;
`,El=()=>n("svg",{xmlns:"http://www.w3.org/2000/svg",width:"20",height:"20",viewBox:"0 0 24 24",children:s("g",{"data-name":"Layer 2",children:[n("rect",{width:"24",height:"24",transform:"rotate(180 12 12)",opacity:"0"}),n("path",{d:"M12 1A10.89 10.89 0 0 0 1 11.77 10.79 10.79 0 0 0 8.52 22c.55.1.75-.23.75-.52v-1.83c-3.06.65-3.71-1.44-3.71-1.44a2.86 2.86 0 0 0-1.22-1.58c-1-.66.08-.65.08-.65a2.31 2.31 0 0 1 1.68 1.11 2.37 2.37 0 0 0 3.2.89 2.33 2.33 0 0 1 .7-1.44c-2.44-.27-5-1.19-5-5.32a4.15 4.15 0 0 1 1.11-2.91 3.78 3.78 0 0 1 .11-2.84s.93-.29 3 1.1a10.68 10.68 0 0 1 5.5 0c2.1-1.39 3-1.1 3-1.1a3.78 3.78 0 0 1 .11 2.84A4.15 4.15 0 0 1 19 11.2c0 4.14-2.58 5.05-5 5.32a2.5 2.5 0 0 1 .75 2v2.95c0 .35.2.63.75.52A10.8 10.8 0 0 0 23 11.77 10.89 10.89 0 0 0 12 1","data-name":"github"})]})});function It(e){return s("a",{href:e.href,target:"_blank",css:cn,rel:"noreferrer",children:[e.icon,n(C,{children:e.text})]})}function X1(){return n(It,{href:"https://github.com/arize-ai/phoenix",icon:n(I,{svg:n(El,{})}),text:"Repository"})}function Y1(){return n(It,{href:"https://docs.arize.com/phoenix",icon:n(I,{svg:n(w.BookOutline,{})}),text:"Documentation"})}function eo(){const{theme:e,setTheme:t}=U(),a=e==="dark";return s("button",{css:cn,onClick:()=>t(a?"light":"dark"),className:"button--reset",children:[n(I,{svg:a?n(w.MoonOutline,{}):n(w.SunOutline,{})}),n(C,{children:a?"Dark":"Light"})]})}function no(){return n(Vn,{to:"/",css:Dl,title:`version: ${window.Config.platformVersion}`,children:n(Ml,{})})}function to({children:e}){return n("nav",{css:Tl,children:e})}function ao({children:e}){const[t,a]=p.useState(!1);return n("nav",{"data-expanded":t,css:Il,onMouseOver:()=>{a(!0)},onMouseOut:()=>{a(!1)},children:e})}function ro(e){return s(oa,{to:e.to,css:cn,children:[e.icon,n(C,{children:e.text})]})}function Fl(e){var t;return typeof e.handle=="object"&&typeof((t=e.handle)==null?void 0:t.crumb)=="function"}function io(){const e=sa(),a=ca().filter(Fl);return n(xa,{onAction:r=>{e(a[Number(r)].pathname)},children:a.map((r,i)=>n(_,{children:r.handle.crumb(r.data)},i))})}const _l=24*60*60*1e3,lo=30*_l,Dt=function(){var e={defaultValue:null,kind:"LocalArgument",name:"datasetId"},t={defaultValue:null,kind:"LocalArgument",name:"description"},a={defaultValue:null,kind:"LocalArgument",name:"metadata"},r={defaultValue:null,kind:"LocalArgument",name:"name"},i=[{alias:null,args:[{fields:[{kind:"Variable",name:"datasetId",variableName:"datasetId"},{kind:"Variable",name:"description",variableName:"description"},{kind:"Variable",name:"metadata",variableName:"metadata"},{kind:"Variable",name:"name",variableName:"name"}],kind:"ObjectValue",name:"input"}],concreteType:"DatasetMutationPayload",kind:"LinkedField",name:"patchDataset",plural:!1,selections:[{alias:null,args:null,concreteType:"Dataset",kind:"LinkedField",name:"dataset",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"description",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"metadata",storageKey:null}],storageKey:null}],storageKey:null}];return{fragment:{argumentDefinitions:[e,t,a,r],kind:"Fragment",metadata:null,name:"EditDatasetFormMutation",selections:i,type:"Mutation",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[e,r,t,a],kind:"Operation",name:"EditDatasetFormMutation",selections:i},params:{cacheID:"d68da97aac0aaababba2324b7d10e250",id:null,metadata:{},name:"EditDatasetFormMutation",operationKind:"mutation",text:`mutation EditDatasetFormMutation(
  $datasetId: GlobalID!
  $name: String!
  $description: String = null
  $metadata: JSON = null
) {
  patchDataset(input: {datasetId: $datasetId, name: $name, description: $description, metadata: $metadata}) {
    dataset {
      name
      description
      metadata
    }
  }
}
`}}}();Dt.hash="17e232f5c22d36d0663f140c00343680";function oo({datasetName:e,datasetId:t,datasetDescription:a,onDatasetEdited:r,onDatasetEditError:i,datasetMetadata:l}){const[o,d]=Z.useMutation(Dt);return n(St,{datasetName:e,datasetDescription:a,datasetMetadata:l,onSubmit:u=>{o({variables:{datasetId:t,...u,metadata:JSON.parse(u.metadata)},onCompleted:()=>{r()},onError:h=>{i(h)}})},isSubmitting:d,submitButtonText:d?"Saving...":"Save",formMode:"edit"})}function so(e){const{value:t}=e;return s("div",{className:"python-code-block",css:m`
        position: relative;
        .copy-to-clipboard-button {
          position: absolute;
          top: var(--ac-global-dimension-size-100);
          right: var(--ac-global-dimension-size-100);
          z-index: 1;
        }
      `,children:[n(gr,{text:t}),n(vl,{value:t})]})}function co({sequenceNumber:e}){return s(Xe,{color:"yellow-1000",children:["#",e]})}var Ke=(e=>(e.ADMIN="ADMIN",e.MEMBER="MEMBER",e))(Ke||{});const Pl=Object.values(Ke);function Vl(e){return typeof e=="string"&&e in Ke}function Nl({onChange:e,role:t,...a}){return n(xe,{label:"Role",className:"role-picker",defaultSelectedKey:t,"aria-label":"User Role",onSelectionChange:r=>{Vl(r)&&e(r)},width:"100%",...a,children:Pl.map(r=>n(_,{children:r.toLocaleLowerCase()},r))})}const _n=4;function uo({onSubmit:e,email:t,username:a,password:r,role:i,isSubmitting:l}){const{control:o,handleSubmit:d,formState:{isDirty:c}}=Ne({defaultValues:{email:t??"",username:a??null,password:r??"",role:i??Ke.MEMBER}});return n("div",{css:m`
        .role-picker {
          width: 100%;
          .ac-dropdown--picker,
          .ac-dropdown-button {
            width: 100%;
          }
        }
      `,children:s(we,{onSubmit:d(e),children:[s(R,{padding:"size-200",children:[n(N,{name:"email",control:o,rules:{required:"Email is required",pattern:{value:/^[^@\s]+@[^@\s]+[.][^@\s]+$/,message:"Invalid email format"}},render:({field:{name:u,onChange:h,onBlur:g,value:f},fieldState:{invalid:L,error:y}})=>n($,{label:"Email",type:"email",name:u,isRequired:!0,description:"The user's email address. Must be unique.",errorMessage:y==null?void 0:y.message,validationState:L?"invalid":"valid",onChange:h,onBlur:g,value:f})}),n(N,{name:"username",control:o,render:({field:{name:u,onChange:h,onBlur:g,value:f},fieldState:{invalid:L,error:y}})=>n($,{label:"Username",name:u,description:"The user's username. Optional.",errorMessage:y==null?void 0:y.message,validationState:L?"invalid":"valid",onChange:h,onBlur:g,value:f==null?void 0:f.toString()})}),n(N,{name:"password",control:o,rules:{required:"Password is required",minLength:{value:_n,message:`Password must be at least ${_n} characters`}},render:({field:{name:u,onChange:h,onBlur:g,value:f},fieldState:{invalid:L,error:y}})=>n($,{label:"Password",type:"password",description:"Password must be at least 4 characters",name:u,errorMessage:y==null?void 0:y.message,validationState:L?"invalid":"valid",onChange:h,onBlur:g,defaultValue:f})}),n(N,{name:"role",control:o,render:({field:{onChange:u,value:h},fieldState:{invalid:g,error:f}})=>n(Nl,{onChange:u,role:h,validationState:g?"invalid":"valid",errorMessage:f==null?void 0:f.message})})]}),n(R,{paddingStart:"size-200",paddingEnd:"size-200",paddingTop:"size-100",paddingBottom:"size-100",borderColor:"dark",borderTopWidth:"thin",children:n(D,{direction:"row",gap:"size-100",justifyContent:"end",children:n(B,{variant:c?"primary":"default",type:"submit",size:"compact",disabled:l,children:l?"Adding...":"Add User"})})})]})})}export{b1 as $,pe as A,l1 as B,S1 as C,Aa as D,R1 as E,ve as F,ft as G,de as H,N1 as I,y1 as J,rn as K,mr as L,p1 as M,v1 as N,C1 as O,t1 as P,Zl as Q,Se as R,re as S,n1 as T,Hl as U,jl as V,ql as W,g1 as X,k1 as Y,u1 as Z,L1 as _,Ja as a,co as a$,x1 as a0,f1 as a1,tr as a2,D1 as a3,V1 as a4,mt as a5,ar as a6,m1 as a7,me as a8,_i as a9,h1 as aA,Xl as aB,i1 as aC,q1 as aD,st as aE,W1 as aF,ll as aG,J1 as aH,j1 as aI,io as aJ,to as aK,no as aL,ro as aM,Y1 as aN,X1 as aO,eo as aP,ao as aQ,Wl as aR,Ql as aS,Z1 as aT,lo as aU,oo as aV,s1 as aW,so as aX,za as aY,U1 as aZ,Fi as a_,Di as aa,Yl as ab,Ni as ac,Ri as ad,Vi as ae,Oi as af,O1 as ag,gr as ah,er as ai,o1 as aj,H1 as ak,xl as al,yl as am,be as an,Q1 as ao,z1 as ap,Bl as aq,rl as ar,$1 as as,B1 as at,G1 as au,K1 as av,A1 as aw,wl as ax,Ei as ay,nr as az,a1 as b,ir as b0,cr as b1,r1 as b2,uo as b3,Ul as b4,e1 as b5,Gl as b6,Jl as b7,c1 as c,U as d,Oa as e,v as f,at as g,P as h,hr as i,E1 as j,F1 as k,_1 as l,T1 as m,I1 as n,P1 as o,je as p,M1 as q,w1 as r,kn as s,ct as t,Oe as u,Fr as v,_r as w,Jn as x,Ar as y,d1 as z};
