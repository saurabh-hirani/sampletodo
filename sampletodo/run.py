''' Wrapper for running the todo api '''

def run():
  ''' Run the todo api '''
  from sampletodo import app
  app.run(host=app.config['SAMPLETODO_HOST'], port=int(app.config['SAMPLETODO_PORT']),
          use_reloader=False, debug=app.config['SAMPLETODO_DEBUG'])

def main():
  ''' Main function for the module '''
  run()

if __name__ == '__main__':
  main()
