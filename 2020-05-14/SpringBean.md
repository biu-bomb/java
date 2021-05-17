```flow
start=>start: 创建对象(构造或工厂)
init=>operation: 成员变量初始化
beanNameAware=>condition: BeanNameAware ?
setBeanName=>operation: setBeanName

beanFactoryAware=>condition: beanFactoryAware ?
setBeanFactory=>operation: setBeanFactory

applicationContextAware=>condition: ApplicationContextAware ?
setApplicationContext=>operation: setApplicationContext

beanPostProcessor=>condition: BeanPostProcessor ?
postProcessBeforeInitialization=>operation: postProcessBeforeInitialization

initializeBean=>condition: InitializeBean ?
afterPropertiesSet=>operation: afterPropertiesSet

initMethod=>condition: init-method ?
invokeInitMethod=>operation: invoke(init-method)

beanPostProcessor2=>condition: BeanPostProcessor ?
postProcessAfterInitialization=>operation: postProcessAfterInitialization

using=>operation: using

close=>condition: context close ?

disposableBean=>condition: DisposableBean ?
destroy=>operation: destroy

destroyMethod=>condition: destroy-method ?
invokeDestroyMethod=>operation: invoke(destroy-method)

end=>end: end

start->init->beanNameAware(yes)->setBeanName->beanFactoryAware(yes)->setBeanFactory
setBeanFactory->applicationContextAware(yes)->setApplicationContext
setApplicationContext->beanPostProcessor(yes)->postProcessBeforeInitialization
postProcessBeforeInitialization->initializeBean(yes)->afterPropertiesSet
afterPropertiesSet->initMethod(yes)->invokeInitMethod
invokeInitMethod->beanPostProcessor2(yes)->postProcessAfterInitialization
postProcessAfterInitialization->using->close(yes)->disposableBean(yes)->destroy
destroy->destroyMethod(yes)->invokeDestroyMethod->end

beanNameAware(no)->beanFactoryAware(no)->applicationContextAware(no)->beanPostProcessor
beanPostProcessor(no)->initializeBean(no)->initMethod(no)->beanPostProcessor2(no)->using
close(no, right)->end
disposableBean(no, left)->destroyMethod(no, left)->end
```

| order | condition               | operatioon                      |
| ----- | ----------------------- | ------------------------------- |
| 1     | BeanNameAware           | setBeanName                     |
| 2     | BeanFactoryAware        | setBeanFactory                  |
| 3     | ApplicationContextAware | setApplicationContext           |
| 4     | BeanPostProcessor       | postProcessBeforeInitialization |
| 5     | InitializingBean        | afterPropertiesSet              |
| 6     | init-method             | init-method                     |
| 7     | BeanPostProcessor       | postProcessAfterInitialization  |
| 8     | DisposableBean          | destroy                         |
| 9     | destroy-method          | destroy-method                  |

