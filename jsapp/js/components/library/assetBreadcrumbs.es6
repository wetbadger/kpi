import React from 'react';
import autoBind from 'react-autobind';
import {bem} from 'js/bem';
import {getAssetDisplayName} from 'js/assetUtils';
import {isOnLibraryRoute} from './libraryUtils';
import myLibraryStore from './myLibraryStore';
import publicCollectionsStore from './publicCollectionsStore';
import {ROOT_BREADCRUMBS} from './libraryConstants';
import {
  ACCESS_TYPES,
  ASSET_TYPES
} from 'js/constants';
import {
  t
} from 'js/utils';

/**
 * @prop asset
 */
class AssetBreadcrumbs extends React.Component {
  constructor(props){
    super(props);
    autoBind(this);
  }

  getRootBreadcrumb() {
    const parentAssetData = this.getParentAssetData();

    if (
      isOnLibraryRoute() &&
      this.props.asset &&
      this.props.asset.asset_type === ASSET_TYPES.collection.id &&
      this.props.asset.access_types !== null &&
      this.props.asset.access_types.includes(ACCESS_TYPES.get('public')) &&
      !this.props.asset.access_types.includes(ACCESS_TYPES.get('subscribed')) &&
      !this.props.asset.access_types.includes(ACCESS_TYPES.get('shared'))
    ) {
      // case for a collection that is public
      return ROOT_BREADCRUMBS.get('public-collections');
    } else if (
      isOnLibraryRoute() &&
      this.props.asset &&
      this.props.asset.asset_type !== ASSET_TYPES.collection.id &&
      parentAssetData &&
      parentAssetData.access_types !== null &&
      parentAssetData.access_types.includes(ACCESS_TYPES.get('public')) &&
      !parentAssetData.access_types.includes(ACCESS_TYPES.get('subscribed')) &&
      !parentAssetData.access_types.includes(ACCESS_TYPES.get('shared'))
    ) {
      // case for an asset that has parent collection that is public
      return ROOT_BREADCRUMBS.get('public-collections');
    } else if (isOnLibraryRoute()) {
      // all the other library assets
      return ROOT_BREADCRUMBS.get('my-library');
    } else {
      return ROOT_BREADCRUMBS.get('projects');
    }
  }

  getParentAssetData() {
    let foundParent = null;
    const parentUid = this.getParentUid();
    if (parentUid) {
      foundParent = myLibraryStore.findAsset(this.getParentUid());
    }
    if (parentUid && !foundParent) {
      foundParent = publicCollectionsStore.findAsset(this.getParentUid());
    }
    return foundParent;
  }

  getParentUid() {
    if (this.props.asset.parent) {
      const parentArr = this.props.asset.parent.split('/');
      const parentAssetUid = parentArr[parentArr.length - 2];
      return parentAssetUid;
    } else {
      return null;
    }
  }

  getParentName() {
    const parentAssetData = this.getParentAssetData();

    if (parentAssetData) {
      return getAssetDisplayName(parentAssetData).final;
    } else {
      return t('Parent Collection');
    }
  }

  getParentHref() {
    const parentUid = this.getParentUid();
    if (parentUid) {
      return `#/library/asset/${this.getParentUid()}`;
    } else {
      return '#';
    }
  }

  render() {
    if (!this.props.asset) {
      return null;
    }

    const assetName = getAssetDisplayName(this.props.asset);
    const rootBreadcrumb = this.getRootBreadcrumb();

    return (
      <bem.Breadcrumbs>
        <bem.Breadcrumbs__crumb href={rootBreadcrumb.href}>
          {rootBreadcrumb.label}
        </bem.Breadcrumbs__crumb>
        <bem.Breadcrumbs__divider/>

        {this.props.asset.parent !== null &&
          <React.Fragment>
          <bem.Breadcrumbs__crumb href={this.getParentHref()}>
            {this.getParentName()}
          </bem.Breadcrumbs__crumb>
          <bem.Breadcrumbs__divider/>
          </React.Fragment>
        }

        <bem.Breadcrumbs__crumb>
          {assetName.final}
        </bem.Breadcrumbs__crumb>
      </bem.Breadcrumbs>
    );
  }
}

export default AssetBreadcrumbs;
