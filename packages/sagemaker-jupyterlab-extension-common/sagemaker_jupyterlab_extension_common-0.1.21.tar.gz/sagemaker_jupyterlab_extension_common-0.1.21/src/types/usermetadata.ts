interface UserMetaData {
  accessToken: string;
  profileArn?: string;
  enabledFeatures?: string[];
}

interface AccessToken {
  idc_access_token: string;
}

interface QDevProfile {
  q_dev_profile_arn: string;
}

interface EnabledFeatures {
  enabled_features: string[];
}

export enum AppEnvironment {
  SMStudio = 'SageMaker Studio',
  SMStudioSSO = 'SageMaker Studio SSO',
  MD = 'MD',
}

export interface LanguageModelConfig {
  model_provider_id?: string | null;
}

export interface AuthDetailsOutput {
  isQDeveloperEnabled: boolean;
  environment: AppEnvironment;
}

export { UserMetaData, AccessToken, QDevProfile, EnabledFeatures };
