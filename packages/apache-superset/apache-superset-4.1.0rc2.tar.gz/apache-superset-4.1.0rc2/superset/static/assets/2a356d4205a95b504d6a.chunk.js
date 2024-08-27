"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[7001],{81788:(e,t,a)=>{a.d(t,{B8:()=>d,TZ:()=>o,mf:()=>l,u7:()=>r});var s=a(31069),n=a(68492);const i=(e,t,a)=>{let s=`api/v1/dashboard/${e}/filter_state`;return t&&(s=s.concat(`/${t}`)),a&&(s=s.concat(`?tab_id=${a}`)),s},o=(e,t,a,o)=>s.Z.put({endpoint:i(e,a,o),jsonPayload:{value:t}}).then((e=>e.json.message)).catch((e=>(n.Z.error(e),null))),r=(e,t,a)=>s.Z.post({endpoint:i(e,void 0,a),jsonPayload:{value:t}}).then((e=>e.json.key)).catch((e=>(n.Z.error(e),null))),d=(e,t)=>s.Z.get({endpoint:i(e,t)}).then((({json:e})=>JSON.parse(e.value))).catch((e=>(n.Z.error(e),null))),l=e=>s.Z.get({endpoint:`/api/v1/dashboard/permalink/${e}`}).then((({json:e})=>e)).catch((e=>(n.Z.error(e),null)))},57001:(e,t,a)=>{a.r(t),a.d(t,{DashboardPage:()=>ie,DashboardPageIdContext:()=>ae,default:()=>oe});var s=a(67294),n=a(11965),i=a(16550),o=a(51995),r=a(61988),d=a(28216),l=a(14114),c=a(38703),u=a(8743),p=a(4305),h=a(50810),g=a(14505),b=a(61337),f=a(27600),m=a(23525),v=a(9467),y=a(81788),w=a(14890),x=a(45697),E=a.n(x),S=a(93185),C=a(14278),D=a(20292),$=a(81255);function _(e){return Object.values(e).reduce(((e,t)=>(t&&t.type===$.dW&&t.meta&&t.meta.chartId&&e.push(t.meta.chartId),e)),[])}var I=a(2275),j=a(3741),U=a(99543),R=a(56967);const F=[$.dW,$.xh,$.t];function O(e){return!Object.values(e).some((({type:e})=>e&&F.includes(e)))}var T=a(35944);const k={actions:E().shape({addSliceToDashboard:E().func.isRequired,removeSliceFromDashboard:E().func.isRequired,triggerQuery:E().func.isRequired,logEvent:E().func.isRequired,clearDataMaskState:E().func.isRequired}).isRequired,dashboardInfo:I.$X.isRequired,dashboardState:I.DZ.isRequired,slices:E().objectOf(I.Rw).isRequired,activeFilters:E().object.isRequired,chartConfiguration:E().object,datasources:E().object.isRequired,ownDataCharts:E().object.isRequired,layout:E().object.isRequired,impressionId:E().string.isRequired,timeout:E().number,userId:E().string};class q extends s.PureComponent{static onBeforeUnload(e){e?window.addEventListener("beforeunload",q.unload):window.removeEventListener("beforeunload",q.unload)}static unload(){const e=(0,r.t)("You have unsaved changes.");return window.event.returnValue=e,e}constructor(e){var t,a;super(e),this.appliedFilters=null!=(t=e.activeFilters)?t:{},this.appliedOwnDataCharts=null!=(a=e.ownDataCharts)?a:{},this.onVisibilityChange=this.onVisibilityChange.bind(this)}componentDidMount(){const e=(0,D.Z)(),{dashboardState:t,layout:a}=this.props,s={is_soft_navigation:j.Yd.timeOriginOffset>0,is_edit_mode:t.editMode,mount_duration:j.Yd.getTimestamp(),is_empty:O(a),is_published:t.isPublished,bootstrap_data_length:e.length},n=(0,R.Z)();n&&(s.target_id=n),this.props.actions.logEvent(j.Wl,s),"hidden"===document.visibilityState&&(this.visibilityEventData={start_offset:j.Yd.getTimestamp(),ts:(new Date).getTime()}),window.addEventListener("visibilitychange",this.onVisibilityChange),this.applyCharts()}componentDidUpdate(){this.applyCharts()}UNSAFE_componentWillReceiveProps(e){const t=_(this.props.layout),a=_(e.layout);this.props.dashboardInfo.id===e.dashboardInfo.id&&(t.length<a.length?a.filter((e=>-1===t.indexOf(e))).forEach((t=>{return this.props.actions.addSliceToDashboard(t,(a=e.layout,s=t,Object.values(a).find((e=>e&&e.type===$.dW&&e.meta&&e.meta.chartId===s))));var a,s})):t.length>a.length&&t.filter((e=>-1===a.indexOf(e))).forEach((e=>this.props.actions.removeSliceFromDashboard(e))))}applyCharts(){const{hasUnsavedChanges:e,editMode:t}=this.props.dashboardState,{appliedFilters:a,appliedOwnDataCharts:s}=this,{activeFilters:n,ownDataCharts:i,chartConfiguration:o}=this.props;(0,S.cr)(S.TT.DashboardCrossFilters)&&!o||(t||(0,U.JB)(s,i,{ignoreUndefined:!0})&&(0,U.JB)(a,n,{ignoreUndefined:!0})||this.applyFilters(),e?q.onBeforeUnload(!0):q.onBeforeUnload(!1))}componentWillUnmount(){window.removeEventListener("visibilitychange",this.onVisibilityChange),this.props.actions.clearDataMaskState()}onVisibilityChange(){if("hidden"===document.visibilityState)this.visibilityEventData={start_offset:j.Yd.getTimestamp(),ts:(new Date).getTime()};else if("visible"===document.visibilityState){const e=this.visibilityEventData.start_offset;this.props.actions.logEvent(j.Ev,{...this.visibilityEventData,duration:j.Yd.getTimestamp()-e})}}applyFilters(){const{appliedFilters:e}=this,{activeFilters:t,ownDataCharts:a}=this.props,s=Object.keys(t),n=Object.keys(e),i=new Set(s.concat(n)),o=((e,t)=>{const a=Object.keys(e),s=Object.keys(t),n=(i=a,o=s,[...i.filter((e=>!o.includes(e))),...o.filter((e=>!i.includes(e)))]).filter((a=>e[a]||t[a]));var i,o;return new Set([...a,...s]).forEach((a=>{(0,U.JB)(e[a],t[a])||n.push(a)})),[...new Set(n)]})(a,this.appliedOwnDataCharts);[...i].forEach((a=>{if(!s.includes(a)&&n.includes(a))o.push(...e[a].scope);else if(n.includes(a)){if((0,U.JB)(e[a].values,t[a].values,{ignoreUndefined:!0})||o.push(...t[a].scope),!(0,U.JB)(e[a].scope,t[a].scope)){const s=(t[a].scope||[]).concat(e[a].scope||[]);o.push(...s)}}else o.push(...t[a].scope)})),this.refreshCharts([...new Set(o)]),this.appliedFilters=t,this.appliedOwnDataCharts=a}refreshCharts(e){e.forEach((e=>{this.props.actions.triggerQuery(!0,e)}))}render(){return this.context.loading?(0,T.tZ)(c.Z,{}):this.props.children}}q.contextType=C.Zn,q.propTypes=k,q.defaultProps={timeout:60,userId:""};const Z=q;var L=a(52256),M=a(97381),P=a(43399),B=a(87915),J=a(74599);const Q=(0,d.$j)((function(e){var t,a,s,n;const{datasources:i,sliceEntities:o,dataMask:r,dashboardInfo:d,dashboardState:l,dashboardLayout:c,impressionId:u,nativeFilters:p}=e;return{timeout:null==(t=d.common)||null==(a=t.conf)?void 0:a.SUPERSET_WEBSERVER_TIMEOUT,userId:d.userId,dashboardInfo:d,dashboardState:l,datasources:i,activeFilters:{...(0,P.De)(),...(0,B.g)({chartConfiguration:null==(s=d.metadata)?void 0:s.chart_configuration,nativeFilters:p.filters,dataMask:r,allSliceIds:l.sliceIds})},chartConfiguration:null==(n=d.metadata)?void 0:n.chart_configuration,ownDataCharts:(0,B.U)(r,"ownState"),slices:o.slices,layout:c.present,impressionId:u}}),(function(e){return{actions:(0,w.DE)({setDatasources:h.Fy,clearDataMaskState:J.sh,addSliceToDashboard:v.Pi,removeSliceFromDashboard:v.rL,triggerQuery:L.triggerQuery,logEvent:M.logEvent},e)}}))(Z);var Y=a(64296);const z=e=>n.iv`
  body {
    h1 {
      font-weight: ${e.typography.weights.bold};
      line-height: 1.4;
      font-size: ${e.typography.sizes.xxl}px;
      letter-spacing: -0.2px;
      margin-top: ${3*e.gridUnit}px;
      margin-bottom: ${3*e.gridUnit}px;
    }

    h2 {
      font-weight: ${e.typography.weights.bold};
      line-height: 1.4;
      font-size: ${e.typography.sizes.xl}px;
      margin-top: ${3*e.gridUnit}px;
      margin-bottom: ${2*e.gridUnit}px;
    }

    h3,
    h4,
    h5,
    h6 {
      font-weight: ${e.typography.weights.bold};
      line-height: 1.4;
      font-size: ${e.typography.sizes.l}px;
      letter-spacing: 0.2px;
      margin-top: ${2*e.gridUnit}px;
      margin-bottom: ${e.gridUnit}px;
    }
  }
`,V=e=>n.iv`
  .header-title a {
    margin: ${e.gridUnit/2}px;
    padding: ${e.gridUnit/2}px;
  }
  .header-controls {
    &,
    &:hover {
      margin-top: ${e.gridUnit}px;
    }
  }
`,N=e=>n.iv`
  .filter-card-popover {
    width: 240px;
    padding: 0;
    border-radius: 4px;

    &.ant-popover-placement-bottom {
      padding-top: ${e.gridUnit}px;
    }

    &.ant-popover-placement-left {
      padding-right: ${3*e.gridUnit}px;
    }

    .ant-popover-inner {
      box-shadow: 0 0 8px rgb(0 0 0 / 10%);
    }

    .ant-popover-inner-content {
      padding: ${4*e.gridUnit}px;
    }

    .ant-popover-arrow {
      display: none;
    }
  }

  .filter-card-tooltip {
    &.ant-tooltip-placement-bottom {
      padding-top: 0;
      & .ant-tooltip-arrow {
        top: -13px;
      }
    }
  }
`,W=e=>n.iv`
  .ant-dropdown-menu.chart-context-menu {
    min-width: ${43*e.gridUnit}px;
  }
  .ant-dropdown-menu-submenu.chart-context-submenu {
    max-width: ${60*e.gridUnit}px;
    min-width: ${40*e.gridUnit}px;
  }
`,K=e=>n.iv`
  a,
  .ant-tabs-tabpane,
  .ant-tabs-tab-btn,
  .superset-button,
  .superset-button.ant-dropdown-trigger,
  .header-controls span {
    &:focus-visible {
      box-shadow: 0 0 0 2px ${e.colors.primary.dark1};
      border-radius: ${e.gridUnit/2}px;
      outline: none;
      text-decoration: none;
    }
    &:not(
        .superset-button,
        .ant-menu-item,
        a,
        .fave-unfave-icon,
        .ant-tabs-tabpane,
        .header-controls span
      ) {
      &:focus-visible {
        padding: ${e.gridUnit/2}px;
      }
    }
  }
`;var A=a(78718),X=a.n(A);const H={},G=()=>{const e=(0,b.rV)(b.dR.DashboardExploreContext,{});return Object.fromEntries(Object.entries(e).filter((([,e])=>!e.isRedundant)))},ee=(e,t)=>{const a=G();(0,b.LS)(b.dR.DashboardExploreContext,{...a,[e]:t})},te=({dashboardPageId:e})=>{const t=(0,d.v9)((({dashboardInfo:t,dashboardState:a,nativeFilters:s,dataMask:n})=>{var i,o,r;return{labelsColor:(null==(i=t.metadata)?void 0:i.label_colors)||H,labelsColorMap:(null==(o=t.metadata)?void 0:o.shared_label_colors)||H,colorScheme:null==a?void 0:a.colorScheme,chartConfiguration:(null==(r=t.metadata)?void 0:r.chart_configuration)||H,nativeFilters:Object.entries(s.filters).reduce(((e,[t,a])=>({...e,[t]:X()(a,["chartsInScope"])})),{}),dataMask:n,dashboardId:t.id,filterBoxFilters:(0,P.De)(),dashboardPageId:e}}),d.wU);return(0,s.useEffect)((()=>(ee(e,t),()=>{ee(e,{...t,isRedundant:!0})})),[t,e]),null},ae=(0,s.createContext)(""),se=(0,s.lazy)((()=>Promise.all([a.e(1216),a.e(6658),a.e(1323),a.e(7802),a.e(8573),a.e(876),a.e(981),a.e(9484),a.e(8109),a.e(1108),a.e(9820),a.e(3197),a.e(7317),a.e(8003),a.e(1090),a.e(9818),a.e(868),a.e(1006),a.e(4717),a.e(452)]).then(a.bind(a,78307)))),ne=document.title,ie=({idOrSlug:e})=>{const t=(0,o.Fg)(),a=(0,d.I0)(),w=(0,i.k6)(),x=(0,s.useMemo)((()=>(0,Y.x0)()),[]),E=(0,d.v9)((({dashboardInfo:e})=>e&&Object.keys(e).length>0)),{addDangerToast:S}=(0,l.e1)(),{result:C,error:D}=(0,u.QU)(e),{result:$,error:_}=(0,u.Es)(e),{result:I,error:j,status:U}=(0,u.JL)(e),R=(0,s.useRef)(!1),F=D||_,O=Boolean(C&&$),{dashboard_title:k,css:q,id:Z=0}=C||{};if((0,s.useEffect)((()=>{const e=()=>{const e=G();(0,b.LS)(b.dR.DashboardExploreContext,{...e,[x]:{...e[x],isRedundant:!0}})};return window.addEventListener("beforeunload",e),()=>{window.removeEventListener("beforeunload",e)}}),[x]),(0,s.useEffect)((()=>{a((0,v.sL)(U))}),[a,U]),(0,s.useEffect)((()=>{Z&&async function(){const e=(0,m.eY)(f.KD.permalinkKey),t=(0,m.eY)(f.KD.nativeFiltersKey),s=(0,m.eY)(f.KD.nativeFilters);let n,i=t||{};if(e){const t=await(0,y.mf)(e);t&&({dataMask:i,activeTabs:n}=t.state)}else t&&(i=await(0,y.B8)(Z,t));s&&(i=s),O&&(R.current||(R.current=!0),a((0,p.Y)({history:w,dashboard:C,charts:$,activeTabs:n,dataMask:i})))}()}),[O]),(0,s.useEffect)((()=>(k&&(document.title=k),()=>{document.title=ne})),[k]),(0,s.useEffect)((()=>"string"==typeof q?(0,g.Z)(q):()=>{}),[q]),(0,s.useEffect)((()=>{j?S((0,r.t)("Error loading chart datasources. Filters may not work correctly.")):a((0,h.Fy)(I))}),[S,I,j,a]),F)throw F;return O&&E?(0,T.BX)(T.HY,{children:[(0,T.tZ)(n.xB,{styles:[N(t),z(t),W(t),K(t),V(t),"",""]}),(0,T.tZ)(te,{dashboardPageId:x}),(0,T.tZ)(ae.Provider,{value:x,children:(0,T.tZ)(Q,{children:(0,T.tZ)(se,{})})})]}):(0,T.tZ)(c.Z,{})},oe=ie},87915:(e,t,a)=>{a.d(t,{U:()=>s,g:()=>n});const s=(e,t)=>Object.values(e).filter((e=>e[t])).reduce(((e,a)=>({...e,[a.id]:t?a[t]:a})),{}),n=({chartConfiguration:e,nativeFilters:t,dataMask:a,allSliceIds:s})=>{const n={};return Object.values(a).forEach((({id:a,extraFormData:i})=>{var o,r,d,l,c,u;const p=null!=(o=null!=(r=null!=(d=null==t||null==(l=t[a])?void 0:l.chartsInScope)?d:null==e||null==(c=e[a])||null==(u=c.crossFilters)?void 0:u.chartsInScope)?r:s)?o:[];n[a]={scope:p,values:i}})),n}},14505:(e,t,a)=>{function s(e){const t="CssEditor-css",a=document.head||document.getElementsByTagName("head")[0],s=document.querySelector(`.${t}`)||function(e){const t=document.createElement("style");return t.className=e,t.type="text/css",t}(t);return"styleSheet"in s?s.styleSheet.cssText=e:s.innerHTML=e,a.appendChild(s),function(){s.remove()}}a.d(t,{Z:()=>s})},8743:(e,t,a)=>{a.d(t,{schemaEndpoints:()=>S.Kt,CN:()=>s.CN,tableEndpoints:()=>E.QD,$O:()=>g,hb:()=>v,QU:()=>y,Es:()=>w,JL:()=>x,L8:()=>D,Xx:()=>S.Xx,SJ:()=>E.SJ,uY:()=>E.uY,zA:()=>E.zA});var s=a(45673),n=a(42190),i=a(67294),o=a(38325),r=a(10362);const d=r.h.injectEndpoints({endpoints:e=>({catalogs:e.query({providesTags:[{type:"Catalogs",id:"LIST"}],query:({dbId:e,forceRefresh:t})=>({endpoint:`/api/v1/database/${e}/catalogs/`,urlParams:{force:t},transformResponse:({json:e})=>e.result.sort().map((e=>({value:e,label:e,title:e})))}),serializeQueryArgs:({queryArgs:{dbId:e}})=>({dbId:e})})})}),{useLazyCatalogsQuery:l,useCatalogsQuery:c,endpoints:u,util:p}=d,h=[];function g(e){const{dbId:t,onSuccess:a,onError:s}=e||{},[n]=l(),r=c({dbId:t,forceRefresh:!1},{skip:!t}),d=(0,o.Z)(((e,t=!1)=>{!e||r.currentData&&!t||n({dbId:e,forceRefresh:t}).then((({isSuccess:e,isError:n,data:i})=>{e&&(null==a||a(i||h,t)),n&&(null==s||s())}))})),u=(0,i.useCallback)((()=>{d(t,!0)}),[t,d]);return(0,i.useEffect)((()=>{d(t,!1)}),[t,d]),{...r,refetch:u}}var b=a(15926);function f({owners:e}){return e?e.map((e=>`${e.first_name} ${e.last_name}`)):null}const m=a.n(b)().encode({columns:["owners.first_name","owners.last_name"],keys:["none"]});function v(e){return(0,n.l6)((0,n.s_)(`/api/v1/chart/${e}?q=${m}`),f)}const y=e=>(0,n.l6)((0,n.s_)(`/api/v1/dashboard/${e}`),(e=>({...e,metadata:e.json_metadata&&JSON.parse(e.json_metadata)||{},position_data:e.position_json&&JSON.parse(e.position_json),owners:e.owners||[]}))),w=e=>(0,n.s_)(`/api/v1/dashboard/${e}/charts`),x=e=>(0,n.s_)(`/api/v1/dashboard/${e}/datasets`);var E=a(23936),S=a(69279);const C=r.h.injectEndpoints({endpoints:e=>({queryValidations:e.query({providesTags:["QueryValidations"],query:({dbId:e,catalog:t,schema:a,sql:s,templateParams:n})=>{let i=n;try{i=JSON.parse(n||"")}catch(e){i=void 0}const o={catalog:t,schema:a,sql:s,...i&&{template_params:i}};return{method:"post",endpoint:`/api/v1/database/${e}/validate_sql/`,headers:{"Content-Type":"application/json"},body:JSON.stringify(o),transformResponse:({json:e})=>e.result}}})})}),{useQueryValidationsQuery:D}=C}}]);
//# sourceMappingURL=2a356d4205a95b504d6a.chunk.js.map