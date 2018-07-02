from collections import OrderedDict


class BaseRobots(object):
    def __init__(self, host):
        self.host = host
        self.rules = list()

    def _allow(self, uri):
        self.rules.append('Allow: %s' % uri)

    def _disallow(self, uri):
        self.rules.append('Disallow: %s' % uri)

    def pre_rules(self):
        rules = OrderedDict()
        return rules

    def compile(self):
        self._disallow('/wrong_domain_404/')
        return self.rules

    def post_rules(self):
        rules = OrderedDict()
        return rules


class YandexRobots(BaseRobots):
    def pre_rules(self):
        rules = super(YandexRobots, self).pre_rules()
        rules['User-agent'] = 'Yandex'
        rules['Clean-param'] = 'order&price_from&price_to&from&q&p&base&offset&form_open&rooms_bath&rooms_bed&' \
                               'yield_to&yield_from&mode&sort&loc'
        return rules

    def post_rules(self):
        rules = super(YandexRobots, self).post_rules()
        rules['Host'] = 'https://%s' % self.host
        return rules


class GoogleRobots(BaseRobots):
    def pre_rules(self):
        rules = super(GoogleRobots, self).pre_rules()
        rules['User-agent'] = 'Googlebot'
        return rules


class WholeRobots(BaseRobots):
    def pre_rules(self):
        rules = super(WholeRobots, self).pre_rules()
        rules['User-agent'] = '*'
        return rules


class RobotsCompiler(object):
    robots = [YandexRobots, GoogleRobots, WholeRobots]

    def compile(self, host):
        rules = []
        for robot in self.robots:
            robot = robot(host)
            rules += ['%s: %s' % rule for rule in robot.pre_rules().items()]
            rules += robot.compile()
            rules += ['%s: %s' % rule for rule in robot.post_rules().items()]
            rules.append('')

        rules.append('Sitemap: https://%s/sitemap.xml' % host)
        return '\n'.join(rules)
