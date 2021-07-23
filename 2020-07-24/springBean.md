# SpringBean生命周期

1. 对象实例创建
2. 对象属性设置
3. 对象创建监听
   1. BeanNameAware.setBeanName
   2. BeanFactoryAware.setBeanFactory
   3. BeanPostProcessor.processBeforeInitialization
   4. InitializeBean.afterPropertiesSet
   5. Init-method
   6. BeanPostProcessor.processAfterInitialization
4. 对象活跃中
5. 对象销毁监听
   1. DisposeBean.destory
   2. Destory-method