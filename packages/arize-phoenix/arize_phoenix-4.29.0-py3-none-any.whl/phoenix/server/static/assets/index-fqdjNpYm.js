import{r as d,j as e,d3 as P,v as s,F,R as v,w as E,aP as S,d4 as L,d5 as R,d6 as a,d7 as w,d8 as z,b as A,d9 as j}from"./vendor-aSQri0vz.js";import{S as C,j as k,Z as $,U as _,t as I,a4 as O}from"./vendor-arizeai-CsdcB1NH.js";import{E as T,L as D,a as N,h as G,M,b as m,D as U,d as B,c as q,e as J,P as K,f as W,T as H,p as V,g,i as Y,j as Z,k as u,l as Q,m as h,n as b,o as X,q as ee,r as re,s as ae,t as te,A as oe,S as ne,F as se}from"./pages-DnbxgoTK.js";import{b5 as ie,d as le,R as ce,b6 as de,b7 as pe}from"./components-BYH03rjA.js";import"./vendor-three-DwGkEfCM.js";import"./vendor-recharts-B0sannek.js";import"./vendor-codemirror-CYHkhs7D.js";(function(){const n=document.createElement("link").relList;if(n&&n.supports&&n.supports("modulepreload"))return;for(const t of document.querySelectorAll('link[rel="modulepreload"]'))c(t);new MutationObserver(t=>{for(const o of t)if(o.type==="childList")for(const i of o.addedNodes)i.tagName==="LINK"&&i.rel==="modulepreload"&&c(i)}).observe(document,{childList:!0,subtree:!0});function l(t){const o={};return t.integrity&&(o.integrity=t.integrity),t.referrerPolicy&&(o.referrerPolicy=t.referrerPolicy),t.crossOrigin==="use-credentials"?o.credentials="include":t.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function c(t){if(t.ep)return;t.ep=!0;const o=l(t);fetch(t.href,o)}})();const x="arize-phoenix-feature-flags",p={__CLEAR__:!0};function me(){const r=localStorage.getItem(x);if(!r)return p;try{const n=JSON.parse(r);return Object.assign({},p,n)}catch{return p}}const f=d.createContext(null);function ge(){const r=v.useContext(f);if(r===null)throw new Error("useFeatureFlags must be used within a FeatureFlagsProvider");return r}function ue(r){const[n,l]=d.useState(me()),c=t=>{localStorage.setItem(x,JSON.stringify(t)),l(t)};return e(f.Provider,{value:{featureFlags:n,setFeatureFlags:c},children:e(he,{children:r.children})})}function he(r){const{children:n}=r,{featureFlags:l,setFeatureFlags:c}=ge(),[t,o]=d.useState(!1);return P("ctrl+shift+f",()=>o(!0)),s(F,{children:[n,e(_,{type:"modal",isDismissable:!0,onDismiss:()=>o(!1),children:t&&e(C,{title:"Feature Flags",children:e(k,{height:"size-1000",padding:"size-100",children:Object.keys(l).map(i=>e($,{isSelected:l[i],onChange:y=>c({...l,[i]:y}),children:i},i))})})})]})}function be(){return e(S,{styles:r=>E`
        body {
          background-color: var(--ac-global-color-grey-75);
          color: var(--ac-global-text-color-900);
          font-family: "Roboto";
          font-size: ${r.typography.sizes.medium.fontSize}px;
          margin: 0;
          #root,
          #root > div[data-overlay-container="true"],
          #root > div[data-overlay-container="true"] > .ac-theme {
            height: 100vh;
          }
        }

        /* Remove list styling */
        ul {
          display: block;
          list-style-type: none;
          margin-block-start: none;
          margin-block-end: 0;
          padding-inline-start: 0;
          margin-block-start: 0;
        }

        /* A reset style for buttons */
        .button--reset {
          background: none;
          border: none;
          padding: 0;
        }
        /* this css class is added to html via modernizr @see modernizr.js */
        .no-hiddenscroll {
          /* Works on Firefox */
          * {
            scrollbar-width: thin;
            scrollbar-color: var(--ac-global-color-grey-300)
              var(--ac-global-color-grey-400);
          }

          /* Works on Chrome, Edge, and Safari */
          *::-webkit-scrollbar {
            width: 14px;
          }

          *::-webkit-scrollbar-track {
            background: var(--ac-global-color-grey-100);
          }

          *::-webkit-scrollbar-thumb {
            background-color: var(--ac-global-color-grey-75);
            border-radius: 8px;
            border: 1px solid var(--ac-global-color-grey-300);
          }
        }

        :root {
          --px-blue-color: ${r.colors.arizeBlue};

          --px-flex-gap-sm: ${r.spacing.margin4}px;
          --px-flex-gap-sm: ${r.spacing.margin8}px;

          --px-section-background-color: ${r.colors.gray500};

          /* An item is a typically something in a list */
          --px-item-background-color: ${r.colors.gray800};
          --px-item-border-color: ${r.colors.gray600};

          --px-spacing-sm: ${r.spacing.padding4}px;
          --px-spacing-med: ${r.spacing.padding8}px;
          --px-spacing-lg: ${r.spacing.padding16}px;

          --px-border-radius-med: ${r.borderRadius.medium}px;

          --px-font-size-sm: ${r.typography.sizes.small.fontSize}px;
          --px-font-size-med: ${r.typography.sizes.medium.fontSize}px;
          --px-font-size-lg: ${r.typography.sizes.large.fontSize}px;

          --px-gradient-bar-height: 8px;

          --px-nav-collapsed-width: 45px;
          --px-nav-expanded-width: 200px;
        }

        .ac-theme--dark {
          --px-primary-color: #9efcfd;
          --px-primary-color--transparent: rgb(158, 252, 253, 0.2);
          --px-reference-color: #baa1f9;
          --px-reference-color--transparent: #baa1f982;
          --px-corpus-color: #92969c;
          --px-corpus-color--transparent: #92969c63;
        }
        .ac-theme--light {
          --px-primary-color: #00add0;
          --px-primary-color--transparent: rgba(0, 173, 208, 0.2);
          --px-reference-color: #4500d9;
          --px-reference-color--transparent: rgba(69, 0, 217, 0.2);
          --px-corpus-color: #92969c;
          --px-corpus-color--transparent: #92969c63;
        }
      `})}const xe=L(R(s(a,{path:"/",errorElement:e(T,{}),children:[e(a,{path:"/login",element:e(D,{})}),s(a,{element:e(N,{}),children:[e(a,{index:!0,loader:G}),s(a,{path:"/model",handle:{crumb:()=>"model"},element:e(M,{}),children:[e(a,{index:!0,element:e(m,{})}),e(a,{element:e(m,{}),children:e(a,{path:"dimensions",children:e(a,{path:":dimensionId",element:e(U,{}),loader:B})})}),e(a,{path:"embeddings",children:e(a,{path:":embeddingDimensionId",element:e(q,{}),loader:J,handle:{crumb:r=>r.embedding.name}})})]}),s(a,{path:"/projects",handle:{crumb:()=>"projects"},element:e(K,{}),children:[e(a,{index:!0,element:e(W,{})}),s(a,{path:":projectId",element:e(H,{}),loader:V,handle:{crumb:r=>r.project.name},children:[e(a,{index:!0,element:e(g,{})}),e(a,{element:e(g,{}),children:e(a,{path:"traces/:traceId",element:e(Y,{})})})]})]}),s(a,{path:"/datasets",handle:{crumb:()=>"datasets"},children:[e(a,{index:!0,element:e(Z,{})}),s(a,{path:":datasetId",loader:u,handle:{crumb:r=>r.dataset.name},children:[s(a,{element:e(Q,{}),loader:u,children:[e(a,{index:!0,element:e(h,{}),loader:b}),e(a,{path:"experiments",element:e(h,{}),loader:b}),e(a,{path:"examples",element:e(X,{}),loader:ee,children:e(a,{path:":exampleId",element:e(re,{})})})]}),e(a,{path:"compare",handle:{crumb:()=>"compare"},loader:ae,element:e(te,{})})]})]}),e(a,{path:"/apis",element:e(oe,{}),handle:{crumb:()=>"APIs"}}),e(a,{path:"/settings",element:e(ne,{}),handle:{crumb:()=>"Settings"}})]})]})),{basename:window.Config.basename});function fe(){return e(w,{router:xe})}function ye(){return e(se,{children:e(ie,{children:e(Pe,{})})})}function Pe(){const{theme:r}=le();return e(O,{theme:r,children:e(z,{theme:I,children:s(A.RelayEnvironmentProvider,{environment:ce,children:[e(be,{}),e(ue,{children:e(de,{children:e(d.Suspense,{children:e(pe,{children:e(fe,{})})})})})]})})})}const Fe=document.getElementById("root"),ve=j.createRoot(Fe);ve.render(e(ye,{}));
