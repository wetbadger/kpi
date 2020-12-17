import _ from 'underscore';
import React from 'react';
import PropTypes from 'prop-types';
import autoBind from 'react-autobind';
import reactMixin from 'react-mixin';
import Reflux from 'reflux';
import DocumentTitle from 'react-document-title';
import {bem} from 'js/bem';
import mixins from 'js/mixins';
import {actions} from 'js/actions';
import assetUtils from 'js/assetUtils';
import {ASSET_TYPES, ACCESS_TYPES} from 'js/constants';
import AssetActionButtons from './assetActionButtons';
import AssetInfoBox from './assetInfoBox';
import AssetPublicButton from './assetPublicButton';
import AssetBreadcrumbs from './assetBreadcrumbs';
import AssetContentSummary from './assetContentSummary';
import CollectionAssetsTable from './collectionAssetsTable';
import {renderLoading} from 'js/components/modalForms/modalHelpers';

class AssetRoute extends React.Component {
  constructor(props) {
    super(props);
    this.state = {asset: false};
    this.unlisteners = [];
    autoBind(this);
  }

  componentDidMount() {
    this.unlisteners.push(
      actions.library.moveToCollection.completed.listen(this.onMoveToCollectionCompleted),
      actions.library.subscribeToCollection.completed.listen(this.onSubscribeToCollectionCompleted),
      actions.library.unsubscribeFromCollection.completed.listen(this.onUnsubscribeFromCollectionCompleted),
      actions.resources.loadAsset.completed.listen(this.onAssetChanged),
      actions.resources.updateAsset.completed.listen(this.onAssetChanged),
      actions.resources.cloneAsset.completed.listen(this.onAssetChanged),
      actions.resources.createResource.completed.listen(this.onAssetChanged),
      actions.resources.deleteAsset.completed.listen(this.onDeleteAssetCompleted)
    );
    this.loadCurrentAsset();
  }

  componentWillUnmount() {
    this.unlisteners.forEach((clb) => {clb();});
  }

  componentWillReceiveProps(nextProps) {
    // trigger loading when switching assets
    if (nextProps.params.uid !== this.props.params.uid) {
      this.setState({asset: false});
      this.loadCurrentAsset();
    }
  }

  loadCurrentAsset() {
    const uid = this.currentAssetID();
    if (uid) {
      actions.resources.loadAsset({id: uid});
    }
  }

  onSubscribeToCollectionCompleted() {
    this.onAssetAccessTypeChanged(true);
  }

  onUnsubscribeFromCollectionCompleted() {
    this.onAssetAccessTypeChanged(false);
  }

  onAssetAccessTypeChanged(setSubscribed) {
    let newAsset = this.state.asset;
    if (setSubscribed) {
      newAsset.access_types.push(ACCESS_TYPES.get('subscribed'));
    } else {
      newAsset.access_types.splice(
        newAsset.access_types.indexOf(ACCESS_TYPES.get('subscribed')),
        1
      );
    }
    this.setState({asset: newAsset});
  }

  onMoveToCollectionCompleted(asset) {
    if (asset.parent === null) {
      this.onAssetRemoved(asset.uid);
    } else {
      this.onAssetChanged(asset);
    }
  }

  onDeleteAssetCompleted({uid}) {
    this.onAssetRemoved(uid);
  }

  onAssetRemoved(assetUid) {
    if (
      this.state.asset &&
      this.state.asset.asset_type === ASSET_TYPES.collection.id &&
      this.state.asset.children.results.length !== 0
    ) {
      let newChildren;
      const index = _.findIndex(this.state.asset.children.results, {uid: assetUid});
      if (index !== -1) {
        newChildren = Array.from(this.state.asset.children.results);
        newChildren.splice(index, 1);
      }

      if (newChildren) {
        const updatedAsset = this.state.asset;
        updatedAsset.children.results = newChildren;
        updatedAsset.children.count = newChildren.length;
        this.setState({asset: updatedAsset});
      }
    }
  }

  onAssetChanged(asset) {
    if (asset.uid === this.currentAssetID()) {
      this.setState({asset: asset});
    } else if (
      this.state.asset &&
      this.state.asset.asset_type === ASSET_TYPES.collection.id &&
      asset.parent === this.state.asset.url
    ) {
      const updatedAsset = this.state.asset;
      const newChildren = Array.from(updatedAsset.children.results);
      const index = _.findIndex(updatedAsset.children.results, {uid: asset.uid});
      if (index === -1) {
        newChildren.push(asset);
      } else {
        newChildren[index] = asset;
      }
      updatedAsset.children.results = newChildren;
      updatedAsset.children.count = newChildren.length;
      this.setState({asset: updatedAsset});
    } else if (
      this.state.asset &&
      this.state.asset.asset_type === ASSET_TYPES.collection.id &&
      asset.parent !== this.state.asset.url
    ) {
      this.onAssetRemoved(asset.uid);
    }
  }

  render() {
    if (this.state.asset === false) {
      return renderLoading();
    }

    const assetName = assetUtils.getAssetDisplayName(this.state.asset);
    const isUserSubscribed = this.state.asset.access_types && this.state.asset.access_types.includes(ACCESS_TYPES.get('subscribed'));

    return (
      <DocumentTitle title={`${assetName.final} | KoboToolbox`}>
        <bem.FormView m='form'>
          <bem.FormView__row>
            <bem.FormView__cell m={['columns', 'columns-right', 'first']}>
              {isUserSubscribed &&
                <bem.FormView__cell m='subscribed-badge'>
                  <i className='k-icon k-icon-folder-subscribed' />
                  {t('Subscribed')}
                </bem.FormView__cell>
              }

              <AssetPublicButton asset={this.state.asset}/>

              <AssetActionButtons asset={this.state.asset}/>
            </bem.FormView__cell>

            <bem.FormView__cell m='first'>
              <AssetBreadcrumbs asset={this.state.asset}/>
            </bem.FormView__cell>

            <AssetInfoBox asset={this.state.asset}/>
          </bem.FormView__row>

          {this.state.asset.asset_type !== ASSET_TYPES.collection.id &&
            <bem.FormView__row>
              <bem.FormView__cell m={['columns', 'first']}>
                <bem.FormView__cell m='label'>
                  {t('Quick look')}
                </bem.FormView__cell>
              </bem.FormView__cell>

              <AssetContentSummary asset={this.state.asset}/>
            </bem.FormView__row>
          }

          {this.state.asset.asset_type === ASSET_TYPES.collection.id &&
            <bem.FormView__row>
              <bem.FormView__cell m={['box']}>
                <CollectionAssetsTable asset={this.state.asset}/>
              </bem.FormView__cell>
            </bem.FormView__row>
          }
        </bem.FormView>
      </DocumentTitle>
    );
  }
}

reactMixin(AssetRoute.prototype, mixins.contextRouter);
reactMixin(AssetRoute.prototype, Reflux.ListenerMixin);

AssetRoute.contextTypes = {
  router: PropTypes.object
};

export default AssetRoute;