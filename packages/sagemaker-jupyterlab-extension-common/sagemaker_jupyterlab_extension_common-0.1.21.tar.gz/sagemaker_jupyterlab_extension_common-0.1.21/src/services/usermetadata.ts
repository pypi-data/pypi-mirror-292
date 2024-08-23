import { JupyterFrontEnd } from '@jupyterlab/application';
import {
  SAGEMAKER_AUTH_DETAILS_ENDPOINT,
  SAGEMAKER_CONTEXT_ENDPOINT,
  SAGEMAKER_AI_CONFIG_ENDPOINT as SAGEMAKER_LANGUAGE_MODEL_CONFIG_ENDPOINT,
} from '../constants';
import { updateSidebarIconToQ } from '../plugins/QDeveloperPlugin/q-developer';
import {
  AccessToken,
  AppEnvironment,
  AuthDetailsOutput,
  LanguageModelConfig,
  QDevProfile,
  UserMetaData,
  EnabledFeatures,
} from '../types/usermetadata';
import { OPTIONS_TYPE, fetchApiResponse } from './fetchapi';

const ENDPOINT = 'api/contents';
const PLUGIN_LOADED_MESSAGE = 'JL_COMMON_PLUGIN_LOADED';
const AWS_DIRECTORY = '.aws';
const SSO_DIRECTORY = AWS_DIRECTORY + '/sso';
const Q_PROFILE_DIRECTORY = AWS_DIRECTORY + '/amazon_q';
const ENABLED_FEATURES_DIRECTORY = AWS_DIRECTORY + '/enabled_features';

const DEFAULT_LANGUAGE_MODEL = 'amazon-q:Q-Developer';

const SM_INTERVAL_TIME = 5 * 60 * 1000; // 5 minutes

class UserMetaDataService {
  private region: string | undefined;

  private smInterval: NodeJS.Timeout | undefined;

  private initialLanguageModel: string | null | undefined;

  constructor(private app: JupyterFrontEnd) {}

  public async initialize() {
    const details = await this.postAuthDetails();
    if (details?.environment === AppEnvironment.SMStudioSSO) {
      if (details.isQDeveloperEnabled) {
        this.initializeSMInterval();
      }
    } else if (details?.environment === AppEnvironment.MD) {
      this.initializeTwoWayIframeCommunication();
    }

    if (!this.initialLanguageModel || this.initialLanguageModel === DEFAULT_LANGUAGE_MODEL) {
      updateSidebarIconToQ(this.app);
    }
  }

  private async initializeSMInterval(): Promise<void> {
    if (!this.smInterval) {
      this.smInterval = setInterval(async () => {
        await this.postAuthDetails();
      }, SM_INTERVAL_TIME);
    }
  }

  private async updateMetadata(metadata: UserMetaData) {
    await this.createDirectoryIfDoesNotExist(AWS_DIRECTORY, '.aws');
    await this.createDirectoryIfDoesNotExist(SSO_DIRECTORY, 'sso');
    await this.createDirectoryIfDoesNotExist(Q_PROFILE_DIRECTORY, 'amazon_q');
    await this.createDirectoryIfDoesNotExist(ENABLED_FEATURES_DIRECTORY, 'enabled_features');

    await this.putMetadataFile(SSO_DIRECTORY, 'idc_access_token', 'json', { idc_access_token: metadata.accessToken });

    await this.putMetadataFile(Q_PROFILE_DIRECTORY, 'q_dev_profile', 'json', {
      q_dev_profile_arn: metadata.profileArn ?? '',
    });

    await this.putMetadataFile(ENABLED_FEATURES_DIRECTORY, 'enabled_features', 'json', {
      enabled_features: metadata.enabledFeatures ?? [],
    });
  }

  public async updateInitialLanguageModelConfig(): Promise<void> {
    const details = await this.postAuthDetails();
    const config = await this.getLanguageModelConfig();
    this.initialLanguageModel = config?.model_provider_id;
    if (details?.environment === AppEnvironment.SMStudio) {
      // in IAM mode, if no model is selected update to Q
      if (!config?.model_provider_id) {
        await this.updateLanguageModelConfig(DEFAULT_LANGUAGE_MODEL);
        this.initialLanguageModel = DEFAULT_LANGUAGE_MODEL;
      }
    } else if (details?.environment === AppEnvironment.SMStudioSSO) {
      // in SSO mode, if Q Developer is enabled and Q is not selected update to Q
      // in SSO mode, if Q Developer is not enabled and no model is selected update to Q
      if (details.isQDeveloperEnabled) {
        if (config?.model_provider_id !== DEFAULT_LANGUAGE_MODEL) {
          await this.updateLanguageModelConfig(DEFAULT_LANGUAGE_MODEL);
          this.initialLanguageModel = DEFAULT_LANGUAGE_MODEL;
        }
      } else {
        if (!config?.model_provider_id) {
          await this.updateLanguageModelConfig(DEFAULT_LANGUAGE_MODEL);
          this.initialLanguageModel = DEFAULT_LANGUAGE_MODEL;
        }
      }
    }
  }

  private async getLanguageModelConfig(): Promise<LanguageModelConfig | undefined> {
    try {
      const response = await fetchApiResponse(SAGEMAKER_LANGUAGE_MODEL_CONFIG_ENDPOINT, OPTIONS_TYPE.GET);
      return (await response.json()) as LanguageModelConfig;
    } catch {
      return undefined;
    }
  }

  private async updateLanguageModelConfig(modelProviderId: string | null): Promise<void> {
    try {
      await fetchApiResponse(
        SAGEMAKER_LANGUAGE_MODEL_CONFIG_ENDPOINT,
        OPTIONS_TYPE.POST,
        JSON.stringify({
          model_provider_id: modelProviderId,
        }),
      );
    } catch {
      return undefined;
    }
  }

  private async postAuthDetails(): Promise<AuthDetailsOutput | undefined> {
    try {
      const response = await fetchApiResponse(SAGEMAKER_AUTH_DETAILS_ENDPOINT, OPTIONS_TYPE.POST);
      return (await response.json()) as AuthDetailsOutput;
    } catch {
      return undefined;
    }
  }

  private async getDirectory(path: string, returnContent?: boolean): Promise<Response | undefined> {
    try {
      return await fetchApiResponse(`${ENDPOINT}/${path}?content=${returnContent ? 1 : 0}`, OPTIONS_TYPE.GET);
    } catch {
      return undefined;
    }
  }

  private putDirectory = async (path: string, name: string): Promise<Response> =>
    await fetchApiResponse(
      `${ENDPOINT}/${path}`,
      OPTIONS_TYPE.PUT,
      JSON.stringify({ type: 'directory', format: 'text', name }),
    );

  private getAllowedDomains = async () => {
    if (!this.region) {
      try {
        const getStudioContextResponse = await fetchApiResponse(SAGEMAKER_CONTEXT_ENDPOINT, OPTIONS_TYPE.GET);
        const response = await getStudioContextResponse.json();
        this.region = response.region;
      } catch (err) {
        // couldnt't fetch context
      }
    }
    const region = this.region;

    return [
      `.v2.${region}.beta.app.iceland.aws.dev`,
      `.v2.niceland-gamma.${region}.on.aws`,
      `.datazone.${region}.on.aws`,
    ];
  };

  private isMessageOriginValid = (event: MessageEvent, allowedDomains: string[]) =>
    this.isLocalhost()
      ? event.origin === 'http://localhost:5173'
      : allowedDomains.some((domain) => event.origin.endsWith(domain));

  private putMetadataFile = async (
    path: string,
    name: string,
    ext: string,
    content: AccessToken | QDevProfile | EnabledFeatures,
  ): Promise<Response> =>
    await fetchApiResponse(
      `${ENDPOINT}/${path ? `${path}/${name}.${ext}` : `/${name}.${ext}`}`,
      OPTIONS_TYPE.PUT,
      JSON.stringify({
        content: JSON.stringify(content),
        format: 'text',
        name: `${name}.${ext}`,
        type: 'file',
      }),
    );

  /**
   * Send a message to the parent window when the plugin is ready to receive user metadata.
   * NOTE: since this message is sent using an unrestricted domain origin, do not pass any sensitive
   * information using this method. This is strictly for handshaking.
   */
  private sendMessageWhenReadyToReceiveUserMetadata(): void {
    window.top?.postMessage(PLUGIN_LOADED_MESSAGE, '*');
  }

  private messageListener = async (event: MessageEvent): Promise<void> => {
    const allowedDomains = await this.getAllowedDomains();

    if (!this.isMessageOriginValid(event, allowedDomains)) return;

    try {
      const metadata = JSON.parse(event.data) as UserMetaData;

      if (!('accessToken' in metadata)) throw new Error('IAM Identity Center access token not found.');

      this.updateMetadata(metadata);
    } catch (err) {
      // create notification service to post error notification in UI.
    }
  };

  private async createDirectoryIfDoesNotExist(path: string, name: string) {
    const exists = await this.getDirectory(path, false);
    if (!exists) {
      await this.putDirectory(path, name);
    }
  }

  private isLocalhost() {
    return ['localhost', '127.0.0.1'].some((condition) => document.location.href.includes(condition));
  }

  /**
   * This method adds an event listener for listening to messages from the parent window
   * and sends a message to the parent window when the message listener has been added.
   * This prevents messages from the parent window from being sent before the plugin has been loaded.
   */
  private initializeTwoWayIframeCommunication(): void {
    window.addEventListener('message', this.messageListener);
    this.sendMessageWhenReadyToReceiveUserMetadata();
  }
}

export { UserMetaDataService };
