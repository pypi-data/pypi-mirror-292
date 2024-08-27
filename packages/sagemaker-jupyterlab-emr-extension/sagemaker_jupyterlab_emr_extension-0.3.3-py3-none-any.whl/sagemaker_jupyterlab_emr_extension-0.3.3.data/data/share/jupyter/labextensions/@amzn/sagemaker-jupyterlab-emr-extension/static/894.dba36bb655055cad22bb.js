"use strict";(self.webpackChunk_amzn_sagemaker_jupyterlab_emr_extension=self.webpackChunk_amzn_sagemaker_jupyterlab_emr_extension||[]).push([[894],{1894:(e,t,n)=>{n.r(t),n.d(t,{default:()=>yn});var a=n(8658),r=n(6029),o=n.n(r),l=n(4083),s=n(1837);const i="SelectedCell",c="HoveredCellClassname",d="SelectAuthContainer",u="SelectEMRAccessRoleContainer";var p;!function(e){e.emrConnect="sagemaker-studio:emr-connect",e.emrServerlessConnect="sagemaker-studio:emr-serverless-connect"}(p||(p={}));const m={width:850,height:500};var g;!function(e){e.name="name",e.id="id",e.status="status",e.creationDateTime="creationDateTime",e.arn="clusterArn"}(g||(g={}));const v="AccessDeniedException",h={tabName:"EMR Clusters",widgetTitle:"Connect to cluster",connectCommand:{label:"Connect",caption:"Connect to a cluster"},connectMessage:{errorTitle:"Error connecting to EMR cluster",successTitle:"Successfully connected to EMR cluster",errorDefaultMessage:"Error connecting to EMR cluster",successDefaultMessage:"Connected to EMR Cluster"},selectRoleErrorMessage:{noEmrExecutionRole:"No available EMR execution role found for the cluster. Please provide one in user profile settings.",noEmrAssumableRole:"No available EMR assumable role found for the cluster. Please provide one in user profile settings."},widgetConnected:"The notebook is connected to",defaultTooltip:"Select a cluster to connect to",widgetHeader:"Select a cluster to connect to. A code block will be added to the active cell and run automatically to establish the connection.",connectedWidgetHeader:"cluster. You can submit new jobs to run on the cluster.",connectButton:"Connect",learnMore:"Learn more",noResultsMatchingFilters:"There are no clusters matching the filter.",radioButtonLabels:{basicAccess:"Http basic authentication",RBAC:"Role-based access control",noCredential:"No credential"},fetchEmrRolesError:"Failed to fetch EMR assumable and execution roles",listClusterError:"Fail to list clusters, refresh the modal or try again later",noCluster:"No clusters are available",permissionError:"The IAM role SageMakerStudioClassicExecutionRole does not have permissions needed to list EMR clusters. Update the role with appropriate permissions and try again. Refer to the",selectCluster:"Select a cluster",selectAssumableRoleTitle:"Select an assumable role for cluster",selectRuntimeExecRoleTitle:"Select EMR runtime execution role for cluster",setUpRuntimeExecRole:"Please make sure you have run the prerequisite steps.",selectAuthTitle:"Select credential type for ",clusterButtonLabel:"Cluster",expandCluster:{MasterNodes:"Master nodes",CoreNodes:"Core nodes",NotAvailable:"Not available",NoTags:"No tags",SparkHistoryServer:"Spark History Server",TezUI:"Tez UI",Overview:"Overview",Apps:"Apps",ApplicationUserInterface:"Application user Interface",Tags:"Tags"},presignedURL:{link:"Link",error:"Error: ",retry:"Retry",sparkUIError:"Spark UI Link is not available or time out. Please try ",sshTunnelLink:"SSH tunnel",or:" or ",viewTheGuide:"view the guide",clusterNotReady:"Cluster is not ready. Please try again later.",clusterNotConnected:"No active cluster connection. Please connect to a cluster and try again.",clusterNotCompatible:"EMR version 5.33+ or 6.3.0+ required for direct Spark UI links. Try a compatible cluster, use "}},E="Cancel",f="Select an execution role",C="Select a cross account assumable role",b={name:"Name",id:"ID",status:"Status",creationTime:"Creation Time",createdOn:"Created On",accountId:"Account ID"},x="EMR Serverless Applications",w="No serverless applications are available",y="AccessDeniedException: Please contact your administrator to get permissions to List Applications",R="AccessDeniedException: Please contact your administrator to get permissions to get selected application details",I={Overview:"Overview",NotAvailable:"Not available",NoTags:"No tags",Tags:"Tags",ReleaseLabel:"Release Label",Architecture:"Architecture",InteractiveLivyEndpoint:"Interactive Livy Endpoint",MaximumCapacity:"Maximum Capacity",Cpu:"Cpu",Memory:"Memory",Disk:"Disk"},S=({handleClick:e,tooltip:t})=>o().createElement("div",{className:"EmrClusterContainer"},o().createElement(l.ToolbarButtonComponent,{className:"EmrClusterButton",tooltip:t,label:h.clusterButtonLabel,onClick:e,enabled:!0}));var A;!function(e){e.tab="Tab",e.enter="Enter",e.escape="Escape",e.arrowDown="ArrowDown"}(A||(A={}));var k=n(8278),N=n(444),T=n(8564);const M={ModalBase:s.css`
  &.jp-Dialog {
    z-index: 1; /* Override default z-index so Dropdown menu is above the Modal */
  }
  .jp-Dialog-body {
    padding: var(--jp-padding-xl);
    .no-cluster-msg {
      padding: var(--jp-cell-collapser-min-height);
      margin: auto;
    }
  }
`,Header:s.css`
  width: 100%;
  display: contents;
  font-size: 0.5rem;
  h1 {
    margin: 0;
  }
`,HeaderButtons:s.css`
  display: flex;
  float: right;
`,ModalFooter:s.css`
  display: flex;
  justify-content: flex-end;
  background-color: var(--jp-layout-color2);
  padding: 12px 24px 12px 24px;
  button {
    margin: 5px;
  }
`,Footer:s.css`
  .jp-Dialog-footer {
    background-color: var(--jp-layout-color2);
    margin: 0;
  }
`,DismissButton:s.css`
  padding: 0;
  border: none;
  cursor: pointer;
`,DialogClassname:s.css`
  .jp-Dialog-content {
    width: 900px;
    max-width: none;
    max-height: none;
    padding: 0;
  }
  .jp-Dialog-header {
    padding: 24px 24px 12px 24px;
    background-color: var(--jp-layout-color2);
  }
  /* Hide jp footer so we can add custom footer with button controls. */
  .jp-Dialog-footer {
    display: none;
  }
`},D=({heading:e,headingId:t="modalHeading",className:n,shouldDisplayCloseButton:a=!1,onClickCloseButton:r,actionButtons:l})=>{let i=null,c=null;return a&&(i=o().createElement(k.z,{className:(0,s.cx)(M.DismissButton,"dismiss-button"),role:"button","aria-label":"close",onClick:r,"data-testid":"close-button"},o().createElement(N.closeIcon.react,{tag:"span"}))),l&&(c=l.map((e=>{const{className:t,component:n,onClick:a,label:r}=e;return n?o().createElement("div",{key:`${(0,T.v4)()}`},n):o().createElement(k.z,{className:t,type:"button",role:"button",onClick:a,"aria-label":r,key:`${(0,T.v4)()}`},r)}))),o().createElement("header",{className:(0,s.cx)(M.Header,n)},o().createElement("h1",{id:t},e),o().createElement("div",{className:(0,s.cx)(M.HeaderButtons,"header-btns")},c,i))};var L=n(1105);const P=({onCloseModal:e,onConnect:t,disabled:n})=>o().createElement("footer",{"data-analytics-type":"eventContext","data-analytics":"JupyterLab",className:M.ModalFooter},o().createElement(k.z,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-Footer-CancelButton",className:"jp-Dialog-button jp-mod-reject jp-mod-styled listcluster-cancel-btn",type:"button",onClick:e},E),o().createElement(k.z,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-Footer-ConnectButton",className:"jp-Dialog-button jp-mod-accept jp-mod-styled listcluster-connect-btn",type:"button",onClick:t,disabled:n},h.connectButton));class U{constructor(e="",t="",n="",a="",r="",o="",l=""){this.partition=e,this.service=t,this.region=n,this.accountId=a,this.resourceInfo=r,this.resourceType=o,this.resourceName=l}static getResourceInfo(e){const t=e.match(U.SPLIT_RESOURCE_INFO_REG_EXP);let n="",a="";return t&&(1===t.length?a=t[1]:(n=t[1],a=t[2])),{resourceType:n,resourceName:a}}static fromArnString(e){const t=e.match(U.ARN_REG_EXP);if(!t)throw new Error(`Invalid ARN format: ${e}`);const[,n,a,r,o,l]=t,{resourceType:s="",resourceName:i=""}=l?U.getResourceInfo(l):{};return new U(n,a,r,o,l,s,i)}static isValid(e){return!!e.match(U.ARN_REG_EXP)}static getArn(e,t,n,a,r,o){return`arn:${e}:${t}:${n}:${a}:${r}/${o}`}}U.ARN_REG_EXP=/^arn:(.*?):(.*?):(.*?):(.*?):(.*)$/,U.SPLIT_RESOURCE_INFO_REG_EXP=/^(.*?)[/:](.*)$/,U.VERSION_DELIMITER="/";const j=({cellData:e})=>{var t,n,a;const r=null===(t=e.status)||void 0===t?void 0:t.state;return"RUNNING"===(null===(n=e.status)||void 0===n?void 0:n.state)||"WAITING"===(null===(a=e.status)||void 0===a?void 0:a.state)?o().createElement("div",null,o().createElement("svg",{width:"10",height:"10"},o().createElement("circle",{cx:"5",cy:"5",r:"5",fill:"green"})),o().createElement("label",{htmlFor:"myInput"},"Running/Waiting")):o().createElement("div",null,o().createElement("label",{htmlFor:"myInput"},r))};var _,$,O,B,F,z,G;!function(e){e.Bootstrapping="BOOTSTRAPPING",e.Running="RUNNING",e.Starting="STARTING",e.Terminated="TERMINATED",e.TerminatedWithErrors="TERMINATED_WITH_ERRORS",e.Terminating="TERMINATING",e.Undefined="UNDEFINED",e.Waiting="WAITING"}(_||(_={})),function(e){e.AllStepsCompleted="All_Steps_Completed",e.BootstrapFailure="Bootstrap_Failure",e.InstanceFailure="Instance_Failure",e.InstanceFleetTimeout="Instance_Fleet_Timeout",e.InternalError="Internal_Error",e.StepFailure="Step_Failure",e.UserRequest="User_Request",e.ValidationError="Validation_Error"}($||($={})),function(e){e[e.SHS=0]="SHS",e[e.TEZUI=1]="TEZUI",e[e.YTS=2]="YTS"}(O||(O={})),function(e){e.None="None",e.Basic_Access="Basic_Access",e.RBAC="RBAC"}(B||(B={})),function(e){e.Success="Success",e.Fail="Fail"}(F||(F={})),function(e){e[e.Content=0]="Content",e[e.External=1]="External",e[e.Notebook=2]="Notebook"}(z||(z={})),function(e){e.Started="STARTED",e.Starting="STARTING",e.Created="CREATED",e.Creating="CREATING",e.Stopped="STOPPED",e.Stopping="STOPPING",e.Terminated="TERMINATED"}(G||(G={}));const H=b;var J=n(2510),V=n(4321);s.css`
  height: 100%;
  position: relative;
`;const W=s.css`
  margin-right: 10px;
`,K=(s.css`
  ${W}
  svg {
    width: 6px;
  }
`,s.css`
  background-color: var(--jp-layout-color2);
  label: ${c};
  cursor: pointer;
`),q=s.css`
  background-color: var(--jp-layout-color3);
  -webkit-touch-callout: none; /* iOS Safari */
  -webkit-user-select: none; /* Safari */
  -khtml-user-select: none; /* Konqueror HTML */
  -moz-user-select: none; /* Old versions of Firefox */
  -ms-user-select: none; /* Internet Explorer/Edge */
  user-select: none; /* Non-prefixed version, currently supported by Chrome, Opera and Firefox */
  label: ${i};
`,X=s.css`
  background-color: var(--jp-layout-color2);
  display: flex;
  padding: var(--jp-cell-padding);
  width: 100%;
  align-items: baseline;
  justify-content: start;
  /* box shadow */
  -moz-box-shadow: inset 0 -15px 15px -15px var(--jp-layout-color3);
  -webkit-box-shadow: inset 0 -15px 15px -15px var(--jp-layout-color3);
  box-shadow: inset 0 -15px 15px -15px var(--jp-layout-color3);
  /* Disable visuals for scroll */
  overflow-x: scroll;
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
  &::-webkit-scrollbar {
    display: none;
  }
`,Y={borderTop:"var(--jp-border-width) solid var(--jp-border-color1)",borderBottom:"var(--jp-border-width) solid var(--jp-border-color1)",borderRight:"var(--jp-border-width) solid var(--jp-border-color1)",display:"flex",boxSizing:"border-box",marginRight:"0px",padding:"2.5px",fontWeight:"initial",textTransform:"capitalize",color:"var(--jp-ui-font-color2)"},Z={display:"flex",flexDirection:"column",height:"max-content"},Q=s.css`
  display: flex;
`,ee={height:"max-content",display:"flex",overflow:"auto",padding:"var(--jp-cell-padding)"},te=({isSelected:e})=>e?o().createElement(N.caretDownIcon.react,{tag:"span"}):o().createElement(N.caretRightIcon.react,{tag:"span"}),ne=({dataList:e,tableConfig:t,selectedId:n,expandedView:a,noResultsView:l,showIcon:i,isLoading:c,columnConfig:d,onRowSelect:u,...p})=>{const m=(0,r.useRef)(null),g=(0,r.useRef)(null),[v,h]=(0,r.useState)(-1),[E,f]=(0,r.useState)(0);(0,r.useEffect)((()=>{var e,t;f((null===(e=null==g?void 0:g.current)||void 0===e?void 0:e.clientHeight)||28),null===(t=m.current)||void 0===t||t.recomputeRowHeights()}),[n,c,t.width,t.height]);const C=({rowData:e,...t})=>e?(0,J.defaultTableCellDataGetter)({rowData:e,...t}):null;return o().createElement(J.Table,{...p,...t,headerStyle:Y,ref:m,headerHeight:28,overscanRowCount:10,rowCount:e.length,rowData:e,noRowsRenderer:()=>l,rowHeight:({index:t})=>e[t].id&&e[t].id===n?E:28,rowRenderer:e=>{const{style:t,key:r,rowData:l,index:i,className:c}=e,d=n===l.id,u=v===i,p=(0,s.cx)(Q,c,{[q]:d,[K]:!d&&u});return d?o().createElement("div",{key:r,ref:g,style:{...t,...Z},onMouseEnter:()=>h(i),onMouseLeave:()=>h(-1),className:p},(0,V.Cx)({...e,style:{width:t.width,...ee}}),o().createElement("div",{className:X},a)):o().createElement("div",{key:r,onMouseEnter:()=>h(i),onMouseLeave:()=>h(-1)},(0,V.Cx)({...e,className:p}))},onRowClick:({rowData:e})=>u(e),rowGetter:({index:t})=>e[t]},d.map((({dataKey:t,label:a,disableSort:r,cellRenderer:l})=>o().createElement(J.Column,{key:t,dataKey:t,label:a,flexGrow:1,width:150,disableSort:r,cellDataGetter:C,cellRenderer:t=>((t,a)=>{const{rowIndex:r,columnIndex:l}=t,s=e[r].id===n,c=0===l;let d=null;return a&&(d=a({row:e[r],rowIndex:r,columnIndex:l,onCellSizeChange:()=>null})),c&&i?o().createElement(o().Fragment,null,o().createElement(te,{isSelected:s})," ",d):d})(t,l)}))))},ae=s.css`
  height: 100%;
  position: relative;
`,re=s.css`
  margin-right: 10px;
`,oe=(s.css`
  ${re}
  svg {
    width: 6px;
  }
`,s.css`
  text-align: center;
  margin: 0;
  position: absolute;
  top: 50%;
  left: 50%;
  margin-right: -50%;
  transform: translate(-50%, -50%);
`),le=(s.css`
  background-color: var(--jp-layout-color2);
  label: ${c};
  cursor: pointer;
`,s.css`
  background-color: var(--jp-layout-color3);
  -webkit-touch-callout: none; /* iOS Safari */
  -webkit-user-select: none; /* Safari */
  -khtml-user-select: none; /* Konqueror HTML */
  -moz-user-select: none; /* Old versions of Firefox */
  -ms-user-select: none; /* Internet Explorer/Edge */
  user-select: none; /* Non-prefixed version, currently supported by Chrome, Opera and Firefox */
  label: ${i};
`,s.css`
  background-color: var(--jp-layout-color2);
  display: flex;
  padding: var(--jp-cell-padding);
  width: 100%;
  align-items: baseline;
  justify-content: start;

  /* box shadow */
  -moz-box-shadow: inset 0 -15px 15px -15px var(--jp-layout-color3);
  -webkit-box-shadow: inset 0 -15px 15px -15px var(--jp-layout-color3);
  box-shadow: inset 0 -15px 15px -15px var(--jp-layout-color3);

  /* Disable visuals for scroll */
  overflow-x: scroll;
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
  &::-webkit-scrollbar {
    display: none;
  }
`,s.css`
  padding: 24px 24px 12px 24px;
`),se=s.css`
  .ReactVirtualized__Table__headerRow {
    display: flex;
  }
  .ReactVirtualized__Table__row {
    display: flex;
    font-size: 12px;
    align-items: center;
  }
`,ie=s.css`
  width: 100%;
  display: flex;
  flex-direction: row;
`,ce=s.css`
  flex-direction: column;
  margin: 0 32px 8px 8px;
  flex: 1 0 auto;
  width: 33%;
`,de=s.css`
  width: 20%;
`,ue=s.css`
  margin-bottom: var(--jp-code-padding);
`,pe=h.expandCluster,me=({clusterData:e})=>{const t=null==e?void 0:e.tags;return(null==t?void 0:t.length)?o().createElement(o().Fragment,null,t.map((e=>o().createElement("div",{className:ue,key:null==e?void 0:e.key},null==e?void 0:e.key,": ",null==e?void 0:e.value)))):o().createElement("div",null,pe.NoTags)},ge=h.expandCluster;var ve=n(1182),he=n(8492);const Ee="/aws/sagemaker/api/emr/describe-cluster",fe="/aws/sagemaker/api/emr/get-on-cluster-app-ui-presigned-url",Ce="/aws/sagemaker/api/emr/create-persistent-app-ui",be="/aws/sagemaker/api/emr/describe-persistent-app-ui",xe="/aws/sagemaker/api/emr/get-persistent-app-ui-presigned-url",we="/aws/sagemaker/api/emr/list-instance-groups",ye="/aws/sagemaker/api/sagemaker/fetch-emr-roles",Re="/aws/sagemaker/api/emr-serverless/get-application",Ie=[200,201];var Se;!function(e){e.POST="POST",e.GET="GET",e.PUT="PUT"}(Se||(Se={}));const Ae=async(e,t,n)=>{const a=ve.ServerConnection.makeSettings(),r=he.URLExt.join(a.baseUrl,e);try{const e=await ve.ServerConnection.makeRequest(r,{method:t,body:n},a);if(!Ie.includes(e.status)&&r.includes("list-clusters"))throw 400===e.status?new Error("permission error"):new Error("Unable to fetch data");return e.json()}catch(e){return{error:e}}},ke=async e=>{var t;const n=JSON.stringify({}),a=await Ae(ye,Se.POST,n);if((null===(t=null==a?void 0:a.EmrAssumableRoleArns)||void 0===t?void 0:t.length)>0)return a.EmrAssumableRoleArns.filter((t=>U.fromArnString(t).accountId===e))},Ne="ApplicationMaster",Te=async(e,t)=>{if(void 0===e)throw new Error("Error describing persistent app UI: Invalid persistent app UI ID");if(t){const n={PersistentAppUIId:e,RoleArn:t},a=JSON.stringify(n);return await Ae(be,Se.POST,a)}const n={PersistentAppUIId:e},a=JSON.stringify(n);return await Ae(be,Se.POST,a)},Me=async e=>await new Promise((t=>setTimeout(t,e))),De=async(e,t)=>{const n={ClusterId:e},a=await ke(t);if((null==a?void 0:a.length)>0)for(const t of a){const n=JSON.stringify({ClusterId:e,RoleArn:t}),a=await Ae(Ee,Se.POST,n);if(void 0!==(null==a?void 0:a.cluster))return a}const r=JSON.stringify(n);return await Ae(Ee,Se.POST,r)},Le=async(e,t)=>{const n={applicationId:e},a=await ke(t);if((null==a?void 0:a.length)>0)for(const t of a){const n=JSON.stringify({applicationId:e,RoleArn:t}),a=await Ae(Re,Se.POST,n);if(void 0!==(null==a?void 0:a.application))return a}const r=JSON.stringify(n);return await Ae(Re,Se.POST,r)},Pe="smsjp--icon-link-external",Ue={link:s.css`
  a& {
    color: var(--jp-content-link-color);
    line-height: var(--jp-custom-ui-text-line-height);
    text-decoration: none;
    text-underline-offset: 1.5px;

    span.${Pe} {
      display: inline;
      svg {
        width: var(--jp-ui-font-size1);
        height: var(--jp-ui-font-size1);
        margin-left: var(--jp-ui-font-size1;
        transform: scale(calc(var(--jp-custom-ui-text-line-height) / 24));
      }
      path {
        fill: var(--jp-ui-font-color1);
      }
    }

    &.sm--content-link {
      text-decoration: underline;
    }

    &:hover:not([disabled]) {
      text-decoration: underline;
    }

    &:focus:not([disabled]),
    &:active:not([disabled]) {
      color: var(--jp-brand-color2);
      .${Pe} path {
        fill: var(--jp-ui-font-color1);
      }
    }

    &:focus:not([disabled]) {
      border: var(--jp-border-width) solid var(--jp-brand-color2);
    }

    &:active:not([disabled]) {
      text-decoration: underline;
    }

    &[disabled] {
      color: var(--jp-ui-font-color3);
      .${Pe} path {
        fill: var(--jp-ui-font-color1);
      }
    }
  }
`,externalIconClass:Pe};var je;!function(e){e[e.Content=0]="Content",e[e.External=1]="External",e[e.Notebook=2]="Notebook"}(je||(je={}));const _e=({children:e,className:t,disabled:n=!1,href:a,onClick:r,type:l=je.Content,hideExternalIcon:i=!1,...c})=>{const d=l===je.External,u={className:(0,s.cx)(Ue.link,t,{"sm-emr-content":l===je.Content}),href:a,onClick:n?void 0:r,target:d?"_blank":void 0,rel:d?"noopener noreferrer":void 0,...c},p=d&&!i?o().createElement("span",{className:Ue.externalIconClass},o().createElement(N.launcherIcon.react,{tag:"span"})):null;return o().createElement("a",{role:"link",...u},e,p)},$e=s.css`
  h2 {
    font-size: var(--jp-ui-font-size1);
    margin-top: 0;
  }
`,Oe=s.css`
  .DataGrid-ContextMenu > div {
    overflow: hidden;
  }
  margin: 12px;
`,Be=s.css`
  padding-bottom: var(--jp-add-tag-extra-width);
`,Fe=s.css`
  background-color: var(--jp-layout-color2);
  display: flex;
  justify-content: flex-end;
  button {
    margin: 5px;
  }
`,ze=s.css`
  text-align: center;
  vertical-align: middle;
`,Ge=s.css`
  .jp-select-wrapper select {
    border: 1px solid;
  }
`,He={ModalBase:$e,ModalBody:Oe,ModalFooter:Fe,ListTable:s.css`
  overflow: hidden;
`,NoHorizontalPadding:s.css`
  padding-left: 0;
  padding-right: 0;
`,RadioGroup:s.css`
  display: flex;
  justify-content: flex-start;
  li {
    margin-right: 20px;
  }
`,ModalHeader:Be,ModalMessage:ze,AuthModal:s.css`
  min-height: none;
`,ListClusterModal:s.css`
  /* so the modal height remains the same visually during and after loading (this number can be changed) */
  min-height: 600px;
`,ConnectCluster:s.css`
  white-space: nowrap;
`,ClusterDescription:s.css`
  display: inline;
`,PresignedURL:s.css`
  line-height: normal;
`,ClusterListModalCrossAccountError:s.css`
  display: flex;
  flex-direction: column;
  padding: 0 0 10px 0;
`,GridWrapper:s.css`
  box-sizing: border-box;
  width: 100%;
  height: 100%;

  & .ReactVirtualized__Grid {
    /* important is required because react virtualized puts overflow style inline */
    overflow-x: hidden !important;
  }

  & .ReactVirtualized__Table__headerRow {
    display: flex;
  }

  & .ReactVirtualized__Table__row {
    display: flex;
    font-size: 12px;
    align-items: center;
  }
`,EmrExecutionRoleContainer:s.css`
  margin-top: 25px;
  width: 90%;
`,Dropdown:s.css`
  margin-top: var(--jp-cell-padding);
`,PresignedURLErrorText:s.css`
  color: var(--jp-error-color1);
`,DialogClassname:s.css`
  .jp-Dialog-content {
    width: 900px;
    max-width: none;
    max-height: none;
    padding: 0;
  }
  .jp-Dialog-header {
    padding: 24px 24px 12px 24px;
    background-color: var(--jp-layout-color2);
  }
  /* Hide jp footer so we can add custom footer with button controls. */
  .jp-Dialog-footer {
    display: none;
  }
`,Footer:s.css`
  .jp-Dialog-footer {
    background-color: var(--jp-layout-color2);
    margin: 0;
  }
`,SelectRole:Ge},Je="Invalid Cluster State",Ve="Missing Cluster ID, are you connected to a cluster?",We="Unsupported cluster version",Ke=({clusterId:e,accountId:t,applicationId:n,persistentAppUIType:a,label:l,onError:i})=>{const[c,d]=(0,r.useState)(!1),[u,p]=(0,r.useState)(!1),m=(0,r.useCallback)((e=>{p(!0),i(e)}),[i]),g=(0,r.useCallback)((e=>{if(!e)throw new Error("Error opening Spark UI: Invalid URL");null!==window.open(e,"_blank","noopener,noreferrer")&&(p(!1),i(null))}),[i]),v=(0,r.useCallback)(((e,t,n)=>{(async(e,t,n)=>{const a=await ke(e);if((null==a?void 0:a.length)>0)for(const e of a){const a={ClusterId:t,OnClusterAppUIType:Ne,ApplicationId:n,RoleArn:e},r=JSON.stringify(a),o=await Ae(fe,Se.POST,r);if(void 0!==(null==o?void 0:o.presignedURL))return o}const r={ClusterId:t,OnClusterAppUIType:Ne,ApplicationId:n},o=JSON.stringify(r);return await Ae(fe,Se.POST,o)})(t,e,n).then((e=>g(null==e?void 0:e.presignedURL))).catch((e=>m(e))).finally((()=>d(!1)))}),[m,g]),E=(0,r.useCallback)(((e,t,n,a)=>{(async e=>{if(void 0===e)throw new Error("Error describing persistent app UI: Invalid persistent app UI ID");const t=U.fromArnString(e).accountId,n=await ke(t);if((null==n?void 0:n.length)>0)for(const t of n){const n={TargetResourceArn:e,RoleArn:t},a=JSON.stringify(n),r=await Ae(Ce,Se.POST,a);if(void 0!==(null==r?void 0:r.persistentAppUIId))return r}const a={TargetResourceArn:e},r=JSON.stringify(a);return await Ae(Ce,Se.POST,r)})(e.clusterArn).then((e=>(async(e,t,n,a)=>{var r;const o=Date.now();let l,s=0;for(;s<=3e4;){const t=await Te(e,a),n=null===(r=null==t?void 0:t.persistentAppUI)||void 0===r?void 0:r.persistentAppUIStatus;if(n&&"ATTACHED"===n){l=t;break}await Me(2e3),s=Date.now()-o}if(null==l)throw new Error("Error waiting for persistent app UI ready: Max attempts reached");return l})(null==e?void 0:e.persistentAppUIId,0,0,null==e?void 0:e.roleArn))).then((e=>(async(e,t,n,a)=>{if(void 0===e)throw new Error("Error getting persistent app UI presigned URL: Invalid persistent app UI ID");if(t){const a={PersistentAppUIId:e,PersistentAppUIType:n,RoleArn:t},r=JSON.stringify(a);return await Ae(xe,Se.POST,r)}const r={PersistentAppUIId:e,PersistentAppUIType:n},o=JSON.stringify(r);return await Ae(xe,Se.POST,o)})(null==e?void 0:e.persistentAppUI.persistentAppUIId,null==e?void 0:e.roleArn,a))).then((e=>g(null==e?void 0:e.presignedURL))).catch((e=>m(e))).finally((()=>d(!1)))}),[m,g]),f=(0,r.useCallback)(((e,t,n,a)=>async()=>{if(d(!0),!t)return d(!1),void m(Ve);const r=await De(t,e).catch((e=>m(e)));if(!r||!(null==r?void 0:r.cluster))return void d(!1);const o=null==r?void 0:r.cluster;if(o.releaseLabel)try{const e=o.releaseLabel.substr(4).split("."),t=+e[0],n=+e[1];if(t<5)return d(!1),void m(We);if(5===t&&n<33)return d(!1),void m(We);if(6===t&&n<3)return d(!1),void m(We)}catch(e){}switch(o.status.state){case _.Running:case _.Waiting:n?v(t,e,n):E(o,e,n,a);break;case _.Terminated:E(o,e,n,a);break;default:d(!1),m(Je)}}),[v,E,m]);return o().createElement(o().Fragment,null,c?o().createElement("span",null,o().createElement(L.CircularProgress,{size:"1rem"})):o().createElement(_e,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-PresignedUrl-Click",className:(0,s.cx)("PresignedURL",He.PresignedURL),onClick:f(t,e,n,a)},u?o().createElement("span",null,l&&l," ",o().createElement("span",{className:(0,s.cx)("PresignedURLErrorText",He.PresignedURLErrorText),onClick:f(t,e,n,a)},"(",h.presignedURL.retry,")")):l||h.presignedURL.link))},qe=s.css`
  cursor: pointer;
  & {
    color: var(--jp-content-link-color);
    text-decoration: none;
    text-underline-offset: 1.5px;
    text-decoration: underline;

    &:hover:not([disabled]) {
      text-decoration: underline;
    }

    &:focus:not([disabled]) {
      border: var(--jp-border-width) solid var(--jp-brand-color2);
    }

    &:active:not([disabled]) {
      text-decoration: underline;
    }

    &[disabled] {
      color: var(--jp-ui-font-color3);
    }
  }
`,Xe=s.css`
  display: flex;
`,Ye=(s.css`
  margin-left: 10px;
`,s.css`
  margin-bottom: var(--jp-code-padding);
`),Ze=h.expandCluster,Qe=({clusterId:e,accountId:t,setIsError:n})=>{const[a]=(0,r.useState)(!1);return o().createElement("div",{className:Xe},o().createElement("div",{className:(0,s.cx)("HistoryLink",qe)},o().createElement(Ke,{clusterId:e,onError:e=>e,accountId:t,persistentAppUIType:"SHS",label:Ze.SparkHistoryServer})),o().createElement(N.launcherIcon.react,{tag:"span"}),a&&o().createElement("span",null,o().createElement(L.CircularProgress,{size:"1rem"})))},et=h.expandCluster,tt=({clusterId:e,accountId:t,setIsError:n})=>{const[a]=o().useState(!1);return o().createElement("div",{className:Xe},o().createElement("div",{className:qe},o().createElement(Ke,{clusterId:e,onError:e=>e,accountId:t,persistentAppUIType:"TEZ",label:et.TezUI})),o().createElement(N.launcherIcon.react,{tag:"span"}),a&&o().createElement("span",null,o().createElement(L.CircularProgress,{size:"1rem"})))},nt=h.expandCluster,at=e=>{const{accountId:t,selectedClusterId:n}=e,[a,l]=(0,r.useState)(!1);return a?o().createElement("div",null,nt.NotAvailable):o().createElement(o().Fragment,null,o().createElement("div",{className:Ye},o().createElement(Qe,{clusterId:n,accountId:t,setIsError:l})),o().createElement("div",{className:Ye},o().createElement(tt,{clusterId:n,accountId:t,setIsError:l})))},rt=h.expandCluster,ot=({clusterArn:e,accountId:t,selectedClusterId:n,clusterData:a})=>{const l=a,[i,c]=(0,r.useState)();return(0,r.useEffect)((()=>{(async e=>{var n,a;const r=JSON.stringify({ClusterId:e}),o=await Ae(we,Se.POST,r);if((null===(n=o.instanceGroups)||void 0===n?void 0:n.length)>0&&(null===(a=o.instanceGroups[0].id)||void 0===a?void 0:a.length)>0)c(o);else{const n=await ke(t);if((null==n?void 0:n.length)>0)for(const t of n){const n=JSON.stringify({ClusterId:e,RoleArn:t}),a=await Ae(we,Se.POST,n);a.instanceGroups.length>0&&a.instanceGroups[0].id&&c(a)}}})(n)}),[n]),o().createElement("div",{"data-analytics-type":"eventContext","data-analytics":"JupyterLab",className:ie},o().createElement("div",{className:ce},o().createElement("h4",null,rt.Overview),o().createElement("div",{className:ue},(e=>{var t;const n=null===(t=null==e?void 0:e.instanceGroups)||void 0===t?void 0:t.find((e=>"MASTER"===(null==e?void 0:e.instanceGroupType)));if(n){const e=n.runningInstanceCount,t=n.instanceType;return`${ge.MasterNodes}: ${e}, ${t}`}return`${ge.MasterNodes}: ${ge.NotAvailable}`})(i)),o().createElement("div",{className:ue},(e=>{var t;const n=null===(t=null==e?void 0:e.instanceGroups)||void 0===t?void 0:t.find((e=>"CORE"===(null==e?void 0:e.instanceGroupType)));if(n){const e=n.runningInstanceCount,t=n.instanceType;return`${ge.CoreNodes}: ${e}, ${t}`}return`${ge.CoreNodes}: ${ge.NotAvailable}`})(i)),o().createElement("div",{className:ue},rt.Apps,": ",(e=>{const t=null==e?void 0:e.applications;return(null==t?void 0:t.length)?t.map(((e,n)=>{const a=n===t.length-1?".":", ";return`${null==e?void 0:e.name} ${null==e?void 0:e.version}${a}`})):`${ge.NotAvailable}`})(l))),o().createElement("div",{className:(0,s.cx)(ce,de)},o().createElement("h4",null,rt.ApplicationUserInterface),o().createElement(at,{selectedClusterId:n,accountId:t,clusterArn:e})),o().createElement("div",{className:ce},o().createElement("h4",null,rt.Tags),o().createElement(me,{clusterData:a})))},lt=h,st=o().createElement("div",{className:ae},o().createElement("p",{className:oe},lt.noResultsMatchingFilters)),it=({clustersList:e,tableConfig:t,clusterManagementListConfig:n,selectedClusterId:a,clusterArn:r,accountId:l,onRowSelect:s,clusterDetails:i,...c})=>{const d=!i&&!1,u=i;return o().createElement(ne,{...c,tableConfig:t,showIcon:!0,dataList:e,selectedId:a,columnConfig:n,isLoading:d,noResultsView:st,onRowSelect:s,expandedView:d?o().createElement("span",null,o().createElement(L.CircularProgress,{size:"1rem"})):o().createElement(ot,{selectedClusterId:a,accountId:l||"",clusterArn:r,clusterData:u,instanceGroupData:void 0})})};n(7960);const ct=e=>"string"==typeof e&&e.length>0,dt=e=>Array.isArray(e)&&e.length>0,ut=(e,t)=>{window&&window.panorama&&window.panorama("trackCustomEvent",{eventType:"eventDetail",eventDetail:e,eventContext:t,timestamp:Date.now()})},pt=(e,t,n)=>{t.execute(e,n)},mt=e=>t=>n=>{pt(e,t,n)},gt=Object.fromEntries(Object.entries(p).map((e=>{const t=e[0],n=e[1];return[t,(a=n,{id:a,createRegistryWrapper:mt(a),execute:(e,t)=>pt(a,e,t)})];var a}))),vt=({onCloseModal:e,selectedCluster:t,selectedServerlessApplication:n,emrConnectRoleData:a,app:l,selectedAssumableRoleArn:i})=>{const c=`${u}`,d=t?a.EmrExecutionRoleArns.filter((e=>U.fromArnString(e).accountId===t.clusterAccountId)):n?a.EmrExecutionRoleArns.filter((e=>U.fromArnString(e).accountId===U.fromArnString(n.arn).accountId)):[],p=d.length?d[0]:void 0,[m,g]=(0,r.useState)(p),v=d.length?o().createElement(N.HTMLSelect,{className:(0,s.cx)(He.SelectRole),options:d,value:m,title:f,onChange:e=>{g(e.target.value)},"data-testid":"select-runtime-exec-role"}):o().createElement("span",{className:"error-msg"},h.selectRoleErrorMessage.noEmrExecutionRole);return o().createElement("div",{className:(0,s.cx)(c,He.ModalBase,He.AuthModal)},o().createElement("div",{className:(0,s.cx)(c,He.ModalBody,He.SelectRole)},v),o().createElement("div",{className:(0,s.cx)(c,He.ModalBody)},o().createElement(_e,{href:t?"https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-steps-runtime-roles.html#emr-steps-runtime-roles-configure":n?"https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/getting-started.html#gs-runtime-role":"",type:je.External},h.setUpRuntimeExecRole)),o().createElement(P,{onCloseModal:e,onConnect:()=>{if(e(),t){const e={clusterId:t.id,language:"python",authType:B.Basic_Access,executionRoleArn:m};i&&Object.assign(e,{crossAccountArn:i}),l.commands.execute(gt.emrConnect.id,e),ut("EMR-Connect-RBAC","JupyterLab")}else if(n){const e={serverlessApplicationId:n.id,executionRoleArn:m,language:"python",assumableRoleArn:i};l.commands.execute(gt.emrServerlessConnect.id,e)}},disabled:void 0===m}))},ht=({onCloseModal:e,selectedCluster:t,emrConnectRoleData:n,app:a,selectedAssumableRoleArn:l})=>{const i=`${d}`,c=`${d}`,[u,p]=(0,r.useState)(B.Basic_Access);return o().createElement("div",{className:(0,s.cx)(i,He.ModalBase,He.AuthModal)},o().createElement("div",{className:(0,s.cx)(c,He.ModalBody)},o().createElement(L.FormControl,null,o().createElement(L.RadioGroup,{"aria-labelledby":"demo-radio-buttons-group-label",defaultValue:B.Basic_Access,value:u,onChange:e=>{p(e.target.value)},name:"radio-buttons-group","data-testid":"radio-button-group",row:!0},o().createElement(L.FormControlLabel,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-SelectAuth-BasicAccess-Click",value:B.Basic_Access,control:o().createElement(L.Radio,null),label:h.radioButtonLabels.basicAccess}),o().createElement(L.FormControlLabel,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-SelectAuth-RBAC-Click",value:B.RBAC,control:o().createElement(L.Radio,null),label:h.radioButtonLabels.RBAC}),!Boolean(null===(m=t.kerberosAttributes)||void 0===m?void 0:m.kdcAdminPassword)&&!(e=>{var t;return Boolean(null===(t=e.configurations)||void 0===t?void 0:t.some((e=>{var t;return"ldap"===(null===(t=null==e?void 0:e.properties)||void 0===t?void 0:t.livyServerAuthType)})))})(t)&&o().createElement(L.FormControlLabel,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-SelectAuth-None-Click",value:B.None,control:o().createElement(L.Radio,null),label:h.radioButtonLabels.noCredential})))),o().createElement(P,{onCloseModal:e,onConnect:()=>{if(u===B.RBAC)e(),bt(n,a,l,t);else{e();const n={clusterId:t.id,authType:u,language:"python"};l&&Object.assign(n,{crossAccountArn:l}),a.commands.execute(gt.emrConnect.id,n),ut("EMR-Connect-Non-RBAC","JupyterLab")}},disabled:!1}));var m},Et=({onCloseModal:e,selectedCluster:t,selectedServerlessApplication:n,emrConnectRoleData:a,app:l})=>{const i=`${u}`,c=t?a.EmrAssumableRoleArns.filter((e=>U.fromArnString(e).accountId===t.clusterAccountId)):n?a.EmrAssumableRoleArns.filter((e=>U.fromArnString(e).accountId===U.fromArnString(n.arn).accountId)):[],d=c.length?c[0]:void 0,[p,m]=(0,r.useState)(d),g=c.length?o().createElement(N.HTMLSelect,{title:C,options:c,value:p,onChange:e=>{m(e.target.value)},"data-testid":"select-assumable-role"}):o().createElement("span",{className:"error-msg"},h.selectRoleErrorMessage.noEmrAssumableRole);return o().createElement("div",{className:(0,s.cx)(i,He.ModalBase,He.AuthModal)},o().createElement("div",{className:(0,s.cx)(i,He.ModalBody,He.SelectRole)},g),o().createElement(P,{onCloseModal:e,onConnect:()=>{e(),t?(Ct(t,a,l,p),ut("EMR-Select-Assumable-Role","JupyterLab")):n&&bt(a,l,p,void 0,n)},disabled:void 0===p}))},ft=(e,t,n,a)=>{let r={};const i=()=>r&&r.resolve();r=new l.Dialog({title:o().createElement(D,{heading:`${h.selectAssumableRoleTitle}`,shouldDisplayCloseButton:!0,onClickCloseButton:i}),body:o().createElement(Et,{onCloseModal:i,selectedCluster:n,selectedServerlessApplication:a,emrConnectRoleData:e,app:t})}),r.addClass((0,s.cx)(M.ModalBase,M.Footer,M.DialogClassname)),r.launch()},Ct=(e,t,n,a)=>{let r={};const i=()=>r&&r.resolve();r=new l.Dialog({title:o().createElement(D,{heading:`${h.selectAuthTitle}"${e.name}"`,shouldDisplayCloseButton:!0,onClickCloseButton:i}),body:o().createElement(ht,{onCloseModal:i,selectedCluster:e,emrConnectRoleData:t,app:n,selectedAssumableRoleArn:a})}),r.addClass((0,s.cx)(M.ModalBase,M.Footer,M.DialogClassname)),r.launch()},bt=(e,t,n,a,r)=>{let i={};const c=()=>i&&i.resolve();i=new l.Dialog({title:o().createElement(D,{heading:`${h.selectRuntimeExecRoleTitle}`,shouldDisplayCloseButton:!0,onClickCloseButton:c}),body:o().createElement(vt,{onCloseModal:c,selectedCluster:a,selectedServerlessApplication:r,emrConnectRoleData:e,app:t,selectedAssumableRoleArn:n})}),i.addClass((0,s.cx)(M.ModalBase,M.Footer,M.DialogClassname)),i.launch()},xt=e=>{const{onCloseModal:t,header:n,app:a}=e,[l,i]=(0,r.useState)([]),[c,d]=(0,r.useState)(!1),[u,p]=(0,r.useState)(""),[v,E]=(0,r.useState)(void 0),[f,C]=(0,r.useState)(),[b,x]=(0,r.useState)(""),[w,y]=(0,r.useState)(!0),R=[{dataKey:g.name,label:H.name,disableSort:!0,cellRenderer:({row:e})=>{var t,n;return((null===(t=e.name)||void 0===t?void 0:t.length)||0)>20?(null===(n=null==e?void 0:e.name)||void 0===n?void 0:n.slice(0,19))+"...":null==e?void 0:e.name}},{dataKey:g.id,label:H.id,disableSort:!0,cellRenderer:({row:e})=>null==e?void 0:e.id},{dataKey:g.status,label:H.status,disableSort:!0,cellRenderer:({row:e})=>o().createElement(j,{cellData:e})},{dataKey:g.creationDateTime,label:H.creationTime,disableSort:!0,cellRenderer:({row:e})=>{var t;return null===(t=null==e?void 0:e.status)||void 0===t?void 0:t.timeline.creationDateTime.split("+")[0].split(".")[0]}},{dataKey:g.arn,label:H.accountId,disableSort:!0,cellRenderer:({row:e})=>{if(null==e?void 0:e.clusterArn)return U.fromArnString(e.clusterArn).accountId}}],I=async(e="",t)=>{try{do{const n=JSON.stringify({ClusterStates:["RUNNING","WAITING"],...e&&{Marker:e},RoleArn:t}),a=await Ae("/aws/sagemaker/api/emr/list-clusters",Se.POST,n);a&&a.clusters&&i((e=>[...new Map([...e,...a.clusters].map((e=>[e.id,e]))).values()])),e=null==a?void 0:a.Marker}while(ct(e))}catch(e){p(e.message)}};(0,r.useEffect)((()=>{(async()=>{var e;try{d(!0);const t=JSON.stringify({}),n=await Ae(ye,Se.POST,t);if((null===(e=null==n?void 0:n.EmrAssumableRoleArns)||void 0===e?void 0:e.length)>0)for(const e of n.EmrAssumableRoleArns)await I("",e);await I(),d(!1)}catch(e){d(!1),p(e.message)}})()}),[]),(0,r.useEffect)((()=>{f&&E((async e=>{const t=S.find((t=>t.id===e));let n="";const a=null==t?void 0:t.clusterArn;a&&U.isValid(a)&&(n=U.fromArnString(a).accountId);const r=await De(e,n);(null==r?void 0:r.cluster.id)&&E(r.cluster)})(f))}),[f]);const S=(0,r.useMemo)((()=>null==l?void 0:l.sort(((e,t)=>{const n=e.name,a=t.name;return null==n?void 0:n.localeCompare(a)}))),[l]),A=(0,r.useCallback)((e=>{const t=S.find((t=>t.id===e));let n="";const a=null==t?void 0:t.clusterArn;return a&&U.isValid(a)&&(n=U.fromArnString(a).accountId),n}),[S]),k=(0,r.useCallback)((e=>{const t=S.find((t=>t.id===e)),n=null==t?void 0:t.clusterArn;return n&&U.isValid(n)?n:""}),[S]),N=(0,r.useCallback)((e=>{const t=null==e?void 0:e.id;t&&t===f?(C(t),x(""),y(!0)):(C(t),x(A(t)),y(!1),ut("EMR-Modal-ClusterRow","JupyterLab"))}),[f,A]);return o().createElement(o().Fragment,null,o().createElement("div",{"data-testid":"list-cluster-view"},u&&o().createElement("span",{className:"no-cluster-msg"},(e=>{const t=o().createElement("a",{href:"https://docs.aws.amazon.com/sagemaker/latest/dg/studio-notebooks-configure-discoverability-emr-cluster.html"},"documentation");return e.includes("permission error")?o().createElement("span",{className:"error-msg"},h.permissionError," ",t):o().createElement("span",{className:"error-msg"},e)})(u)),c?o().createElement("span",null,o().createElement(L.CircularProgress,{size:"1rem"})):dt(l)?o().createElement("div",{className:(0,s.cx)(le,"modal-body-container")},n,o().createElement(o().Fragment,null,o().createElement("div",{className:(0,s.cx)(se,"grid-wrapper")},o().createElement(it,{clustersList:S,selectedClusterId:null!=f?f:"",clusterArn:k(null!=f?f:""),accountId:A(null!=f?f:""),tableConfig:m,clusterManagementListConfig:R,onRowSelect:N,clusterDetails:v})))):o().createElement("div",{className:"no-cluster-msg"},h.noCluster),o().createElement(P,{onCloseModal:t,onConnect:async()=>{try{const e=await Ae(ye,Se.POST,void 0);if("MISSING_AWS_ACCOUNT_ID"===e.CallerAccountId)throw new Error("Failed to get caller account Id");if(!v)throw new Error("Error in getting cluster details");if(!b)throw new Error("Error in getting cluster account Id");v.clusterAccountId=b,v.clusterAccountId===e.CallerAccountId?(t(),Ct(v,e,a)):(t(),ft(e,a,v)),ut("EMR-Select-Cluster","JupyterLab")}catch(e){p(e.message)}},disabled:w})))},wt=b,yt=({status:e})=>e===G.Started||e===G.Stopped||e===G.Created?o().createElement("div",null,o().createElement("svg",{width:"10",height:"10"},o().createElement("circle",{cx:"5",cy:"5",r:"5",fill:"green"})),o().createElement("label",{htmlFor:"myInput"},e)):o().createElement("div",null,o().createElement("label",{htmlFor:"myInput"},e)),Rt=s.css`
  flex-direction: column;
  margin: 0 0 8px 8px;
  flex: 1 0 auto;
  width: 33%;
`,It=I;var St=n(4439),At=n.n(St);const kt=I,Nt=({applicationData:e})=>{const t=null==e?void 0:e.tags;return At().isEmpty(t)?o().createElement("div",null,kt.NoTags):o().createElement(o().Fragment,null,Object.entries(t).map((([e,t])=>o().createElement("div",{className:ue,key:e},e,": ",t))))},Tt=I,Mt=({applicationData:e})=>e&&o().createElement(o().Fragment,null,o().createElement("div",{className:Rt},o().createElement("h4",null,Tt.Overview),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.architecture;return t?`${It.Architecture}: ${t}`:`${It.Architecture}: ${It.NotAvailable}`})(e)),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.releaseLabel;return t?`${It.ReleaseLabel}: ${t}`:`${It.ReleaseLabel}: ${It.NotAvailable}`})(e)),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.livyEndpointEnabled;return"True"===t?`${It.InteractiveLivyEndpoint}: Enabled`:"False"===t?`${It.InteractiveLivyEndpoint}: Disabled`:`${It.InteractiveLivyEndpoint}: ${It.NotAvailable}`})(e))),o().createElement("div",{className:Rt},o().createElement("h4",null,Tt.MaximumCapacity),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.maximumCapacityCpu;return t?`${It.Cpu}: ${t}`:`${It.Cpu}: ${It.NotAvailable}`})(e)),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.maximumCapacityMemory;return t?`${It.Memory}: ${t}`:`${It.Memory}: ${It.NotAvailable}`})(e)),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.maximumCapacityDisk;return t?`${It.Disk}: ${t}`:`${It.Disk}: ${It.NotAvailable}`})(e))),o().createElement("div",{className:Rt},o().createElement("h4",null,Tt.Tags),o().createElement(Nt,{applicationData:e}))),Dt=h,Lt=o().createElement("div",{className:ae},o().createElement("p",{className:oe},Dt.noResultsMatchingFilters)),Pt=({applicationsList:e,tableConfig:t,applicationManagementListConfig:n,selectedApplicationId:a,applicationArn:r,accountId:l,onRowSelect:s,applicationDetails:i,applicationDetailsLoading:c,...d})=>o().createElement(ne,{...d,tableConfig:t,showIcon:!0,dataList:e,selectedId:a,columnConfig:n,isLoading:c,noResultsView:Lt,onRowSelect:s,expandedView:c?o().createElement("span",null,o().createElement(L.CircularProgress,{size:"1rem"})):o().createElement(Mt,{applicationData:i})}),Ut=s.css`
  &:not(:active) {
    color: var(--jp-ui-font-color2);
  }
`,jt=s.css`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  color: var(--jp-error-color0);
  background-color: var(--jp-error-color3);
`,_t=s.css`
  font-size: 12px;
  font-style: normal;
  font-weight: 500;
  line-height: 150%;
  margin: unset;
  flex-grow: 1;
`,$t=e=>{const[t,n]=(0,r.useState)(!1),{error:a}=e;return(0,r.useEffect)((()=>{n(!1)}),[a]),a&&!t?o().createElement("div",{className:jt},o().createElement("p",{className:_t},a),o().createElement(L.IconButton,{sx:{padding:"4px",color:"inherit"},onClick:()=>{n(!0)}},o().createElement(N.closeIcon.react,{elementPosition:"center",tag:"span"}))):null},Ot=e=>{const{onCloseModal:t,header:n,app:a}=e,[l,i]=(0,r.useState)([]),[c,d]=(0,r.useState)(!1),[u,p]=(0,r.useState)(""),[h,E]=(0,r.useState)(void 0),[f,C]=(0,r.useState)(!1),[b,x]=(0,r.useState)(),[I,S]=(0,r.useState)(""),[A,k]=(0,r.useState)(!0),N=[{dataKey:g.name,label:wt.name,disableSort:!0,cellRenderer:({row:e})=>{var t,n;return((null===(t=e.name)||void 0===t?void 0:t.length)||0)>20?(null===(n=null==e?void 0:e.name)||void 0===n?void 0:n.slice(0,19))+"...":null==e?void 0:e.name}},{dataKey:g.id,label:wt.id,disableSort:!0,cellRenderer:({row:e})=>null==e?void 0:e.id},{dataKey:g.status,label:wt.status,disableSort:!0,cellRenderer:({row:e})=>o().createElement(yt,{status:e.status})},{dataKey:g.creationDateTime,label:wt.creationTime,disableSort:!0,cellRenderer:({row:e})=>{var t;return null===(t=null==e?void 0:e.createdAt)||void 0===t?void 0:t.split("+")[0].split(".")[0]}},{dataKey:g.arn,label:wt.accountId,disableSort:!0,cellRenderer:({row:e})=>{if(null==e?void 0:e.arn)return U.fromArnString(e.arn).accountId}}],T=async(e="",t)=>{do{const n=JSON.stringify({states:[G.Started,G.Created,G.Stopped],...e&&{nextToken:e},roleArn:t}),a=await Ae("/aws/sagemaker/api/emr-serverless/list-applications",Se.POST,n);a&&a.applications&&i((e=>[...new Map([...e,...a.applications].map((e=>[e.id,e]))).values()])),e=null==a?void 0:a.nextToken,a.code||a.errorMessage?(d(!1),a.code===v?p(y):p(`${a.code}: ${a.errorMessage}`)):p("")}while(ct(e))};(0,r.useEffect)((()=>{(async(e="")=>{var t;try{d(!0);const e=JSON.stringify({}),n=await Ae(ye,Se.POST,e);if(await T(),(null===(t=null==n?void 0:n.EmrAssumableRoleArns)||void 0===t?void 0:t.length)>0)for(const e of n.EmrAssumableRoleArns)await T("",e);d(!1)}catch(e){d(!1),p(e.message)}})()}),[]);const M=(0,r.useMemo)((()=>null==l?void 0:l.sort(((e,t)=>{const n=e.name,a=t.name;return null==n?void 0:n.localeCompare(a)}))),[l]);(0,r.useEffect)((()=>{b&&E((async e=>{C(!0),k(!0);const t=l.find((t=>t.id===e));let n="";const a=null==t?void 0:t.arn;a&&U.isValid(a)&&(n=U.fromArnString(a).accountId);const r=await Le(e,n);E(r.application),r.code||r.errorMessage?(C(!1),r.code===v?p(R):p(`${r.code}: ${r.errorMessage}`)):p(""),C(!1),k(!1)})(b))}),[b]);const D=(0,r.useCallback)((e=>{const t=M.find((t=>t.id===e));let n="";const a=null==t?void 0:t.arn;return a&&U.isValid(a)&&(n=U.fromArnString(a).accountId),n}),[M]),j=(0,r.useCallback)((e=>{const t=M.find((t=>t.id===e)),n=null==t?void 0:t.arn;return n&&U.isValid(n)?n:""}),[M]),_=(0,r.useCallback)((e=>{const t=null==e?void 0:e.id;t&&t===b?(x(t),S(""),k(!0)):(x(t),S(D(t)),k(!1))}),[b,D]);return o().createElement(o().Fragment,null,o().createElement("div",{"data-testid":"list-serverless-applications-view"},u&&o().createElement($t,{error:u}),c?o().createElement("span",null,o().createElement(L.CircularProgress,{size:"1rem"})):dt(l)?o().createElement("div",{className:(0,s.cx)(le,"modal-body-container")},n,o().createElement(o().Fragment,null,o().createElement("div",{className:(0,s.cx)(se,"grid-wrapper")},o().createElement(Pt,{applicationsList:M,selectedApplicationId:null!=b?b:"",applicationArn:j(null!=b?b:""),accountId:D(null!=b?b:""),tableConfig:m,applicationManagementListConfig:N,onRowSelect:_,applicationDetails:h,applicationDetailsLoading:f})))):o().createElement("div",{className:"no-cluster-msg"},w),o().createElement(P,{onCloseModal:t,onConnect:async()=>{try{const e=await Ae(ye,Se.POST);if("MISSING_AWS_ACCOUNT_ID"===e.CallerAccountId)throw new Error("Failed to get caller account Id");if(!h)throw new Error("Error in getting serverless application details");if(!I)throw new Error("Error in getting serverless application account Id");I!==e.CallerAccountId?(t(),ft(e,a,void 0,h)):(t(),bt(e,a,void 0,void 0,h))}catch(e){p(e.message)}},disabled:A})))};function Bt(e){const{children:t,value:n,index:a,...r}=e;return o().createElement("div",{role:"tabpanel",hidden:n!==a,...r},n===a&&o().createElement("div",null,t))}function Ft(e){const[t,n]=o().useState(0);return o().createElement("div",null,o().createElement("div",null,o().createElement(L.Tabs,{value:t,onChange:(e,t)=>{n(t)}},o().createElement(L.Tab,{className:(0,s.cx)(Ut),label:x}),o().createElement(L.Tab,{className:(0,s.cx)(Ut),label:h.tabName}))),o().createElement(Bt,{value:t,index:0},o().createElement(Ot,{onCloseModal:e.onCloseModal,header:e.header,app:e.app})),o().createElement(Bt,{value:t,index:1},o().createElement(xt,{onCloseModal:e.onCloseModal,header:e.header,app:e.app})))}class zt{constructor(e,t,n){this.disposeDialog=e,this.header=t,this.app=n}render(){return o().createElement(r.Suspense,{fallback:null},o().createElement(Ft,{onCloseModal:this.disposeDialog,app:this.app,header:this.header}))}}const Gt=(e,t,n)=>new zt(e,t,n);var Ht;!function(e){e["us-east-1"]="us-east-1",e["us-east-2"]="us-east-2",e["us-west-1"]="us-west-1",e["us-west-2"]="us-west-2",e["us-gov-west-1"]="us-gov-west-1",e["us-gov-east-1"]="us-gov-east-1",e["us-iso-east-1"]="us-iso-east-1",e["us-isob-east-1"]="us-isob-east-1",e["ca-central-1"]="ca-central-1",e["eu-west-1"]="eu-west-1",e["eu-west-2"]="eu-west-2",e["eu-west-3"]="eu-west-3",e["eu-central-1"]="eu-central-1",e["eu-north-1"]="eu-north-1",e["eu-south-1"]="eu-south-1",e["ap-east-1"]="ap-east-1",e["ap-south-1"]="ap-south-1",e["ap-southeast-1"]="ap-southeast-1",e["ap-southeast-2"]="ap-southeast-2",e["ap-southeast-3"]="ap-southeast-3",e["ap-northeast-3"]="ap-northeast-3",e["ap-northeast-1"]="ap-northeast-1",e["ap-northeast-2"]="ap-northeast-2",e["sa-east-1"]="sa-east-1",e["af-south-1"]="af-south-1",e["cn-north-1"]="cn-north-1",e["cn-northwest-1"]="cn-northwest-1",e["me-south-1"]="me-south-1"}(Ht||(Ht={}));const Jt=e=>(e=>e===Ht["cn-north-1"]||e===Ht["cn-northwest-1"])(e)?"https://docs.amazonaws.cn":"https://docs.aws.amazon.com",Vt=({clusterName:e})=>{const t=Jt(Ht["us-west-2"]);return o().createElement("div",{className:(0,s.cx)(He.ModalHeader,"list-cluster-modal-header")},(()=>{let t;if(e){const n=o().createElement("span",{className:He.ConnectCluster},e),a=`${h.widgetConnected} `,r=` ${h.connectedWidgetHeader} `;t=o().createElement("div",{className:(0,s.cx)(He.ClusterDescription,"list-cluster-description")},a,n,r)}else t=`${h.widgetHeader} `;return t})(),o().createElement(_e,{href:`${t}/sagemaker/latest/dg/studio-notebooks-emr-cluster.html`,type:je.External},h.learnMore))};class Wt extends l.ReactWidget{constructor(e,t){super(),this.updateConnectedCluster=e=>{this._connectedCluster=e,this.update()},this.getToolTip=()=>this._connectedCluster?`${h.widgetConnected} ${this._connectedCluster.name} cluster`:h.defaultTooltip,this.clickHandler=async()=>{let e={};const t=()=>e&&e.resolve();e=new l.Dialog({title:o().createElement(D,{heading:h.widgetTitle,shouldDisplayCloseButton:!0,onClickCloseButton:t,className:"list-cluster-modal-header"}),body:Gt(t,this.listClusterHeader(),this._appContext).render()}),e.handleEvent=t=>{"keydown"===t.type&&(({keyboardEvent:e,onEscape:t,onShiftTab:n,onShiftEnter:a,onTab:r,onEnter:o})=>{const{key:l,shiftKey:s}=e;s?l===A.tab&&n?n():l===A.enter&&a&&a():l===A.tab&&r?r():l===A.enter&&o?o():l===A.escape&&t&&t()})({keyboardEvent:t,onEscape:()=>e.reject()})},e.addClass((0,s.cx)(M.ModalBase,M.Footer,M.DialogClassname)),e.launch()},this.listClusterHeader=()=>{var e;return o().createElement(Vt,{clusterName:null===(e=this._connectedCluster)||void 0===e?void 0:e.name})},this._selectedCluster=null,this._appContext=t,this._connectedCluster=null,this._kernelId=null}get kernelId(){return this._kernelId}get selectedCluster(){return this._selectedCluster}updateKernel(e){this._kernelId!==e&&(this._kernelId=e,this.kernelId&&this.update())}render(){return o().createElement(S,{handleClick:this.clickHandler,tooltip:this.getToolTip()})}}const Kt=e=>null!=e,qt=async(e,t,n=!0)=>new Promise((async(r,o)=>{if(t){const l=t.content,s=l.model,i=t.context.sessionContext,{metadata:c}=s.sharedModel.toJSON(),d={cell_type:"code",metadata:c,source:e},u=l.activeCell,p=u?l.activeCellIndex:0;if(s.sharedModel.insertCell(p,d),l.activeCellIndex=p,n)try{await a.NotebookActions.run(l,i)}catch(e){o(e)}const m=[];for(const e of u.outputArea.node.children)m.push(e.innerHTML);r({html:m,cell:u})}o("No notebook panel")})),Xt=e=>{const t=e.shell.widgets("main");let n=t.next().value;for(;n;){if(n.hasClass("jp-NotebookPanel")&&n.isVisible)return n;n=t.next().value}return null};var Yt=n(7704),Zt=n.n(Yt);const Qt=e=>{const t=h.presignedURL.sshTunnelLink;return e?o().createElement(_e,{href:e,type:je.External,hideExternalIcon:!0},t):o().createElement("span",{className:(0,s.cx)("PresignedURLErrorText",He.PresignedURLErrorText)},t)},en=()=>o().createElement(_e,{href:"https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-ssh-tunnel.html",type:je.External},h.presignedURL.viewTheGuide),tn=({sshTunnelLink:e,error:t})=>o().createElement(o().Fragment,null,(()=>{switch(t){case Je:return o().createElement("span",{className:(0,s.cx)("PresignedURLErrorText",He.PresignedURLErrorText)},o().createElement("b",null,h.presignedURL.error),h.presignedURL.clusterNotReady);case Ve:return o().createElement("span",{className:(0,s.cx)("PresignedURLErrorText",He.PresignedURLErrorText)},o().createElement("b",null,h.presignedURL.error),h.presignedURL.clusterNotConnected);case We:return(e=>o().createElement("span",{className:(0,s.cx)("PresignedURLErrorText",He.PresignedURLErrorText)},o().createElement("b",null,h.presignedURL.error),h.presignedURL.clusterNotCompatible,Qt(e),h.presignedURL.or,en()))(e);default:return(e=>o().createElement("span",null,o().createElement("span",{className:(0,s.cx)("PresignedURLErrorText",He.PresignedURLErrorText)},o().createElement("b",null,h.presignedURL.error),h.presignedURL.sparkUIError),Qt(e),o().createElement("span",{className:(0,s.cx)("PresignedURLErrorText",He.PresignedURLErrorText)},h.presignedURL.or),en()))(e)}})()),nn=(e,t)=>{var n;for(let a=0;a<e.childNodes.length;a++)if(null===(n=e.childNodes[a].textContent)||void 0===n?void 0:n.includes(t))return a;return-1},an=e=>{try{let t=e.lastElementChild;for(;t;)e.removeChild(t),t=e.lastElementChild}catch(e){}},rn="YARN Application ID",on="Spark UI",ln="--cluster-id",sn="--assumable-role-arn",cn="%info",dn="%configure",un={childList:!0,subtree:!0};class pn{constructor(e){this.trackedPanels=new Set,this.trackedCells=new Set,this.notebookTracker=e,this.triggers=[mn,cn,dn],this.kernelChanged=!1,this.lastConnectedClusterId=null,this.lastConnectedAccountId=void 0}run(){this.notebookTracker.currentChanged.connect(((e,t)=>{t&&(this.isTrackedPanel(t)||(t.context.sessionContext.kernelChanged.connect(((e,t)=>{this.kernelChanged=!0})),t.context.sessionContext.iopubMessage.connect(((e,n)=>{!this.isTrackedPanel(t)||this.kernelChanged?(n?(this.trackPanel(t),this.handleExistingSparkWidgetsOnPanelLoad(t)):this.stopTrackingPanel(t),this.kernelChanged=!1):this.isTrackedPanel(t)&&this.checkMessageForEmrConnectAndInject(n,t)}))))}))}isTrackedCell(e){return this.trackedCells.has(e)}trackCell(e){this.trackedCells.add(e)}stopTrackingCell(e){this.trackedCells.delete(e)}isTrackedPanel(e){return this.trackedPanels.has(e)}trackPanel(e){this.trackedPanels.add(e)}stopTrackingPanel(e){this.trackedPanels.delete(e)}handleExistingSparkWidgetsOnPanelLoad(e){e.revealed.then((()=>{const t=new RegExp(this.triggers.join("|"));((e,t)=>{var n;const a=null===(n=null==e?void 0:e.content)||void 0===n?void 0:n.widgets;return null==a?void 0:a.filter((e=>{const n=e.model.sharedModel;return t.test(n.source)}))})(e,t).forEach((e=>{if(this.containsSparkMagicTable(e.outputArea.node)){const t=e.model.sharedModel,n=this.getClusterId(t.source),a=this.getAccountId(t.source);this.injectPresignedURL(e,n,a)}else this.injectPresignedURLOnTableRender(e)}))}))}checkMessageForEmrConnectAndInject(e,t){if("execute_input"!==e.header.msg_type)return;const n=e.content.code;var a;this.codeContainsTrigger(n)&&(a=n,t.content.widgets.filter((e=>e.model.sharedModel.source.includes(a)))).forEach((e=>{this.injectPresignedURLOnTableRender(e)}))}codeContainsTrigger(e){const t=this.triggers.filter((t=>e.includes(t)));return dt(t)}getParameterFromEmrConnectCommand(e,t){const n=e.split(" "),a=n.indexOf(t);if(!(-1===a||a+1>n.length-1))return n[a+1]}getClusterId(e){return e&&e.includes(ln)?this.getParameterFromEmrConnectCommand(e,ln)||null:this.lastConnectedClusterId}getAccountId(e){if(!e)return this.lastConnectedAccountId;if(e.includes(cn))return this.lastConnectedAccountId;if(e.includes(sn)){const t=this.getParameterFromEmrConnectCommand(e,sn);return void 0!==t?U.fromArnString(t).accountId:void 0}}getSparkMagicTableBodyNodes(e){const t=Array.from(e.getElementsByTagName("tbody"));return dt(t)?t.filter((e=>this.containsSparkMagicTable(e))):[]}containsSparkMagicTable(e){var t;return(null===(t=e.textContent)||void 0===t?void 0:t.includes(rn))&&e.textContent.includes(on)}isSparkUIErrorRow(e){var t;return e instanceof HTMLTableRowElement&&(null===(t=e.textContent)||void 0===t?void 0:t.includes(h.presignedURL.error))||!1}injectSparkUIErrorIntoNextTableRow(e,t,n,a){var r;const l=this.isSparkUIErrorRow(t.nextSibling);if(null===a)return void(l&&(null===(r=t.nextSibling)||void 0===r||r.remove()));let s;if(l?(s=t.nextSibling,an(s)):s=((e,t)=>{let n=1,a=!1;for(let r=1;r<e.childNodes.length;r++)if(e.childNodes[r].isSameNode(t)){n=r,a=!0;break}if(!a)return null;const r=n+1<e.childNodes.length?n+1:-1;return e.insertRow(r)})(e,t),!s)return;const i=s.insertCell(),c=t.childElementCount;i.setAttribute("colspan",c.toString()),i.style.textAlign="left",i.style.background="#212121";const d=o().createElement(tn,{sshTunnelLink:n,error:a});Zt().render(d,i)}injectPresignedURL(e,t,n){var a;const r=e.outputArea.node,l=e.model.sharedModel,s=this.getSparkMagicTableBodyNodes(r);if(!dt(s))return!1;if(l.source.includes(dn)&&s.length<2)return!1;for(let e=0;e<s.length;e++){const r=s[e],l=r.firstChild,i=nn(l,on),c=nn(l,"Driver log"),d=nn(l,rn),u=l.getElementsByTagName("th")[c];if(l.removeChild(u),-1===i||-1===d)break;for(let e=1;e<r.childNodes.length;e++){const l=r.childNodes[e],s=l.childNodes[i];l.childNodes[c].remove();const u=null===(a=s.getElementsByTagName("a")[0])||void 0===a?void 0:a.href;s.hasChildNodes()&&an(s);const p=l.childNodes[d].textContent||void 0,m=document.createElement("div");s.appendChild(m);const g=o().createElement(Ke,{clusterId:t,applicationId:p,onError:e=>this.injectSparkUIErrorIntoNextTableRow(r,l,u,e),accountId:n});Zt().render(g,m)}}return!0}injectPresignedURLOnTableRender(e){this.isTrackedCell(e)||(this.trackCell(e),new MutationObserver(((t,n)=>{for(const a of t)if("childList"===a.type)try{const t=e.model.sharedModel,a=this.getClusterId(t.source),r=this.getAccountId(t.source);if(this.injectPresignedURL(e,a,r)){this.stopTrackingCell(e),n.disconnect(),this.lastConnectedClusterId=a,this.lastConnectedAccountId=r;break}}catch(t){this.stopTrackingCell(e),n.disconnect()}})).observe(e.outputArea.node,un))}}const mn="%sm_analytics emr connect",gn=h,vn={id:"@sagemaker-studio:EmrCluster",autoStart:!0,optional:[a.INotebookTracker],activate:async(e,t)=>{null==t||new pn(t).run(),e.docRegistry.addWidgetExtension("Notebook",new hn(e)),e.commands.addCommand(gt.emrConnect.id,{label:e=>gn.connectCommand.label,isEnabled:()=>!0,isVisible:()=>!0,caption:()=>gn.connectCommand.caption,execute:async t=>{try{const{clusterId:n,authType:a,language:r,crossAccountArn:o,executionRoleArn:l,notebookPanelToInjectCommandInto:s}=t,i="%load_ext sagemaker_studio_analytics_extension.magics",c=Kt(r)?`--language ${r}`:"",d=Kt(o)?`--assumable-role-arn ${o}`:"",u=Kt(l)?`--emr-execution-role-arn ${l}`:"",p=`${i}\n${mn} --verify-certificate False --cluster-id ${n} --auth-type ${a} ${c} ${d} ${u}`,m=s||Xt(e);await qt(p,m)}catch(e){throw e.message,e}}}),e.commands.addCommand(gt.emrServerlessConnect.id,{label:e=>gn.connectCommand.label,isEnabled:()=>!0,isVisible:()=>!0,caption:()=>gn.connectCommand.caption,execute:async t=>{try{const{serverlessApplicationId:n,language:a,assumableRoleArn:r,executionRoleArn:o,notebookPanelToInjectCommandInto:l}=t,s="%load_ext sagemaker_studio_analytics_extension.magics",i=Kt(a)?` --language ${a}`:"",c=`${s}\n%sm_analytics emr-serverless connect --application-id ${n}${i}${Kt(r)?` --assumable-role-arn ${r}`:""}${Kt(o)?` --emr-execution-role-arn ${o}`:""}`,d=l||Xt(e);await qt(c,d)}catch(e){throw e.message,e}}})}};class hn{constructor(e){this.appContext=e}createNew(e,t){const n=(a=e.sessionContext,r=this.appContext,new Wt(a,r));var a,r;return e.context.sessionContext.kernelChanged.connect((e=>{var t;const a=null===(t=e.session)||void 0===t?void 0:t.kernel;e.iopubMessage.connect(((e,t)=>{((e,t,n,a)=>{if(n)try{if(e.content.text){const{isConnSuccess:t,clusterId:r}=(e=>{let t,n=!1;if(e.content.text){const a=JSON.parse(e.content.text);if("sagemaker-analytics"!==a.namespace)return{};t=a.cluster_id,n=a.success}return{isConnSuccess:n,clusterId:t}})(e);t&&n.id===r&&a(n)}}catch(e){return}})(t,0,n.selectedCluster,n.updateConnectedCluster)})),a&&a.spec.then((e=>{e&&e.metadata&&n.updateKernel(a.id)})),n.updateKernel(null)})),e.toolbar.insertBefore("kernelName","emrCluster",n),n}}var En=n(8916);const fn={errorTitle:"Unable to connect to EMR cluster/EMR serverless application",defaultErrorMessage:"Something went wrong when connecting to the EMR cluster/EMR serverless application.",invalidRequestErrorMessage:"A request to attach the EMR cluster/EMR serverless application to the notebook is invalid.",invalidClusterErrorMessage:"EMR cluster ID is invalid."},Cn={invalidApplicationErrorMessage:"EMR Serverless Application ID is invalid."};let bn=!1;const xn=async e=>(0,l.showErrorMessage)(fn.errorTitle,{message:e}),wn=async e=>{const t=await e.commands.execute("notebook:create-new");await new Promise((e=>{t.sessionContext.kernelChanged.connect(((t,n)=>{e(n)}))})),await(2e3,new Promise((e=>setTimeout(e,2e3))))},yn=[vn,{id:"@sagemaker-studio:DeepLinking",requires:[En.IRouter],autoStart:!0,activate:async(e,t)=>{const{commands:n}=e,a="emrCluster:open-notebook-for-deeplinking";n.addCommand(a,{execute:()=>(async(e,t)=>{if(!bn)try{const{search:n}=e.current;if(!n)return void await xn(fn.invalidRequestErrorMessage);t.restored.then((async()=>{const{clusterId:e,applicationId:a,accountId:r}=he.URLExt.queryStringToObject(n);if(!e&&!a)return void await xn(fn.invalidRequestErrorMessage);const o=await Ae(ye,Se.POST,void 0);o&&!(null==o?void 0:o.error)?e?await(async(e,t,n,a)=>{const r=await De(e,n);if(!r||!(null==r?void 0:r.cluster))return void await xn(fn.invalidClusterErrorMessage);const o=r.cluster;await wn(t),n?(o.clusterAccountId=n,ft(a,t,o)):(o.clusterAccountId=a.CallerAccountId,Ct(o,a,t))})(e,t,r,o):a&&await(async(e,t,n,a)=>{const r=await Le(e,n);if(!r||!(null==r?void 0:r.application))return void await xn(Cn.invalidApplicationErrorMessage);const o=r.application;await wn(t),n?ft(a,t,void 0,o):bt(a,t,void 0,void 0,o)})(a,t,r,o):await xn(h.fetchEmrRolesError)}))}catch(e){return void await xn(fn.defaultErrorMessage)}finally{bn=!0}})(t,e)}),t.register({command:a,pattern:new RegExp("[?]command=attach-emr-to-notebook"),rank:10})}}]}}]);