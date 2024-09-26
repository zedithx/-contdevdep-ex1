# Use the official lightweight Ruby image.
# https://hub.docker.com/_/ruby
FROM ruby:3.3.1

# Set working directory
WORKDIR /app

# Copy gemfiles for bundle installs
COPY Gemfile Gemfile.lock ./

RUN gem install bundler && bundle install

# copy the current directory contents into container
COPY . /app

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run service2.py when the container launches
CMD ["ruby", "service.rb"]