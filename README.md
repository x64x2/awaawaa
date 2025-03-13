## PomPom

a toki pona language translation tool written in ruby


### Installation

```bash
$ gem install pompom
```

Or in your Gemfile:

```ruby
gem 'pompom'
```

## Batch translation 

```ruby
# multiple strings
PomPom.translate(['Hello', 'Goodbye'], to: :toki pona) # => ["pona", "lala"]
```
