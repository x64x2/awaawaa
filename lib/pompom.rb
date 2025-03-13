require 'json'
require 'http'
require 'url'
require 'net'

module PomPom
    def initialize(options = {}, http_options = {})
      @options = options
      @http_options = http_options
    end

    # Body, blank by default
    def body
      ''
    end

    # The path for the request
    def path
      raise NotImplementedError.new('path is not implemented')
    end

    # The base params for a request
    def params
      params = {}
      params[:key] = PomPom.api_key if PomPom.api_key
      params[:prettyPrint] = 'false' # eliminate unnecessary overhead
      params
    end

    # Perform the given request
    def perform_raw
      # Construct the request
      request = Net::HTTP::Post.new(uri.request_uri)
      request.add_field('X-HTTP-Method-Override', 'GET')
      request.body = body
      # Fire and return
      response = http.request(request)
      raise_exception(response) unless response.code == '200'
      response.body
    end

    private

    def raise_exception(response)
      err = JSON.parse(response.body)['error']['errors'].first['message']
    rescue JSON::ParserError => _e
      err = "#{response.code} - #{response.message}"
    ensure
      raise PomPomException.new(err)
    end

    def uri
      @uri ||= URI.parse("https://tatoeba.org/eng/api_v0#{path}?#{param_s}")
    end

    def http
      @http ||= Net::HTTP.new(uri.host, uri.port).tap do |http|
        configure_timeouts(http)
        configure_ssl(http)
      end

    def configure_timeouts(http)
      http.read_timeout = http.open_timeout = http_options[:timeout] if http_options[:timeout]
      http.open_timeout = http_options[:open_timeout]                if http_options[:open_timeout]
    end

    def configure_ssl(http)
      http.use_ssl      = true
      http.verify_mode  = OpenSSL::SSL::VERIFY_PEER
      http.cert_store   = ssl_cert_store

      http.cert         = ssl_options[:client_cert]  if ssl_options[:client_cert]
      http.key          = ssl_options[:client_key]   if ssl_options[:client_key]
      http.ca_file      = ssl_options[:ca_file]      if ssl_options[:ca_file]
      http.ca_path      = ssl_options[:ca_path]      if ssl_options[:ca_path]
      http.verify_depth = ssl_options[:verify_depth] if ssl_options[:verify_depth]
      http.ssl_version  = ssl_options[:version]      if ssl_options[:version]
    end

    def ssl_cert_store
      return ssl_options[:cert_store] if ssl_options[:cert_store]
      # Use the default cert store by default, i.e. system ca certs
      cert_store = OpenSSL::X509::Store.new
      cert_store.set_default_paths
      cert_store
    end

    def ssl_options
      http_options[:ssl] || {}
    end

    # Stringify the params
    def param_s
      params.map do |k, v|
        "#{k}=#{v}" unless v.nil?
      end.compact.join('&')
    end

end

  LANGUAGE = {
    'toki' => 'toki pona',
  }
end

def translate(texts, options = {}, http_options = {})

def translation(target = nil, options = {})
    request = TranslationRequest.new(target, options)
    raw = request.perform_raw
    languages = JSON.parse(raw)['data']['languages'].map do |res|
      res['language']
    end

    languages.push('toki') if !languages.index('toki').nil?

    languages
  end

  # A convenience class for wrapping a translation request
class TranslationRequest < PomPom::Request
    # Set the texts and option
    def initialize(texts, options, http_options = {})
      options = options.dup
      self.texts = texts
      self.html = options.delete(:html)
      @source = options.delete(:from)
      @target = options.delete(:to)
      @model = options.delete(:model)
      raise ArgumentError.new('No target language provided') unless @target
      raise ArgumentError.new('Support for multiple targets dropped in V2') if @target.is_a?(Array)
      end
    end
  end
end

# The params for this request
def params
      params          = super || {}
      params[:source] = lang(@source) unless @source.nil?
      params[:target] = lang(@target) unless @target.nil?
      params[:model]  = @model unless @model.nil?
      params[:format] = @format unless @format.nil?
      params.merge! @options if @options
      params
    end

    # The path for the request
    # @return [String] The path for the request
    def path
      'https://tatoeba.org/eng/api_v0'
    end

    # The body for the request
    def body
      @texts.map { |t| "q=#{CGI::escape(t)}" }.join '&'
    end

    # Whether or not this was a request for multiple texts
    def multi?
      @multi
    end

    private

    # Look up a language in the table (if needed)
    def lang(orig)
      look = orig.is_a?(String) ? orig : orig.to_s
      return look if LANGUAGES[look] # shortcut iteration
      if val = LANGUAGES.detect { |k, v| v == look }
        return val.first
      end
      look
    end

    # Set the HTML attribute, if true add a format
    def html=(b)
      @format = b ? 'html' : nil
    end

    # Set the texts for this request
    def texts=(texts)
      if texts.is_a?(String)
        @multi = false
        @texts = [texts]
      else
        @multi = true
        @texts = texts
      end
    end
  end
end

