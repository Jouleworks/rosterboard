import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {KeyValuePipe, NgForOf, NgIf} from "@angular/common";
import {FormControl, FormGroup, FormsModule, ReactiveFormsModule} from "@angular/forms";
import {HttpClient, HttpClientModule, HttpHandler} from "@angular/common/http";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NgForOf, NgIf, ReactiveFormsModule, FormsModule, HttpClientModule, KeyValuePipe],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'rosterboard-setup-ui';
  steps = [
    { header: 'Database Credentials', subtext: 'Connect to your Database' },
    { header: 'Application Settings', subtext: 'Setup your application settings' },
    { header: 'Admin Account', subtext: 'Setup a superuser' },
    { header: 'Install Rosterboard', subtext: 'Install Rosterboard' },
    { header: 'Finish', subtext: 'View results and finish Installation' },
  ]
  step: number = 1;

  constructor(private http: HttpClient) {
  }

  dbForm = new FormGroup({
    db_host: new FormControl(''),
    db_port: new FormControl(''),
    db_user: new FormControl(''),
    db_pass: new FormControl(''),
    db_name: new FormControl(''),
  });

  configGenerator = {
    SECRET_KEY: {type: 'string', value: 'your-secret-key', description: 'Enter a secret key between 32 and 64 characters long for your application. This is used to encrypt passwords and login sessions, among other things. Do not share this value with anyone.'},
    ALLOWED_HOSTS: {type: 'string', description: 'Enter the domain this program is hosted on. Do not include a port.', value: 'localhost'},
    APP_DEBUG: {type: 'boolean', description: 'Enables developer mode. DO NOT USE IN PRODUCTION ENVIRONMENTS.', value: false},
    CORS_ALLOWED_ORIGINS: {type: 'string', description: 'Allowed domains for API/Remote Access? (Hint: If unsure, make this the domain of your website)', value: '*'},
    CHANNEL_LAYERS_REDIS_URLS: {type: 'string', description: 'Redis URL for Multiplayer/Live Update Support. There should be at least one redis URL here. To connect to multiple redis instances, separate the urls by commas.', value: 'redis://localhost:6379/0'},
    ALLOW_REGISTRATION: {type: 'boolean', description: 'Allow users to register for their own account without Admin Intervention?', value: true},
  }

  containerVariables = {
    'db_host': 'localhost',
    'db_port': '5432',
    'db_user': 'postgres',
    'db_pass': 'postgres',
    'db_name': 'rosterboard',
  }

  superuser = {
    username: '',
    password: '',
    email: '',
  }

  credentialType: string = '';
  dbUrl: string = '';
  checkingDb: boolean = false;
  confirmPassword: string = '';
  generatedConfig: string = '';


  fillInDB(mthd: string) {
    switch (mthd) {
      case 'url':
        // use containerVariables
          this.dbUrl = `postgresql://${this.containerVariables['db_user']}:${this.containerVariables['db_pass']}@${this.containerVariables['db_host']}:${this.containerVariables['db_port']}/${this.containerVariables['db_name']}`;
        break;
      case 'form':
        this.dbUrl = `postgresql://${this.containerVariables['db_user']}:${this.containerVariables['db_pass']}@${this.containerVariables['db_host']}:${this.containerVariables['db_port']}/${this.containerVariables['db_name']}`;
        this.dbForm.patchValue(this.containerVariables);
        break;
        default:
          break;
    }

    this.configGenerator.CHANNEL_LAYERS_REDIS_URLS.value = 'redis://rosterboard-redis-db-1:6379/0';
    this.configGenerator.ALLOWED_HOSTS.value = document.location.hostname;
  }

  randomString(length: number, chars: string): string {
    var mask = '';
    if (chars.indexOf('a') > -1) mask += 'abcdefghijklmnopqrstuvwxyz';
    if (chars.indexOf('A') > -1) mask += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (chars.indexOf('#') > -1) mask += '0123456789';
    var result = '';
    for (var i = length; i > 0; --i) result += mask[Math.floor(Math.random() * mask.length)];
    return result;
  }

  testDatabaseCredentials(mthd: string) {
    this.checkingDb = true;
    switch (mthd) {
      case 'url':
        // use containerVariables
        // dburl set already via ngModel
        break;
      case 'form':
        this.dbUrl = `postgresql://${this.dbForm.value['db_user']}:${this.dbForm.value['db_pass']}@${this.dbForm.value['db_host']}:${this.dbForm.value['db_port']}/${this.dbForm.value['db_name']}`;
        break;
      default:
        break;
    }

    this.http.post('/test/database/', { database_url: this.dbUrl }).subscribe(
        (res: any) => {
          this.checkingDb = false;
          if(res.result){
            this.configGenerator.ALLOWED_HOSTS.value = document.location.hostname;
            this.configGenerator.CORS_ALLOWED_ORIGINS.value = document.location.hostname;
            //generate a random string of 32 characters for SECRET_KEY
            this.configGenerator.SECRET_KEY.value = this.randomString(64, 'aA#');
            this.step = 2;
          }else{
            alert("Failed to connect to the database. "+res.errors);
          }
        },
        (err: any) => {
          this.checkingDb = false;
          alert("Failed to connect to the database. A critical failure has occured.");
        }
    )

  }

  cleanupSetup2() {
    this.configGenerator.ALLOWED_HOSTS.value = this.configGenerator.ALLOWED_HOSTS.value.replace(/^\/+|\/+$/g, '').replace(/^https?:/, '').replace(/^http?:/, '');
    this.configGenerator.CORS_ALLOWED_ORIGINS.value = this.configGenerator.CORS_ALLOWED_ORIGINS.value.replace(/^\/+|\/+$/g, '').replace(/^https?:/, '').replace(/^http?:/, '');
    this.step = 3;
  }

  cleanupStep3() {
    // check to make sure password has 8 characters, contains at least one uppercase letter, one lowercase letter, one number, and one special character
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if(!passwordRegex.test(this.superuser.password)){
      alert("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.");
      return;
    }

    // check to make sure email is a valid email address
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if(!emailRegex.test(this.superuser.email)){
      alert("Please enter a valid email address.");
      return;
    }

    // make sure a username has been entered that is longer than 3 characters
    if(this.superuser.username.length < 3){
      alert("Username must be at least 3 characters long.");
      return;
    }

    // check to make sure passwords match
    if(this.superuser.password!== this.confirmPassword){
      alert("Passwords do not match.");
      return;
    }

    this.generatedConfig = `[settings]
SECRET_KEY="${this.configGenerator.SECRET_KEY.value}"
ALLOWED_HOSTS="${this.configGenerator.ALLOWED_HOSTS.value}"
CORS_ALLOWED_ORIGINS="${this.configGenerator.CORS_ALLOWED_ORIGINS.value}"
CHANNEL_LAYERS_REDIS_URLS="${this.configGenerator.CHANNEL_LAYERS_REDIS_URLS.value}"
ALLOW_REGISTRATION='${this.configGenerator.ALLOW_REGISTRATION.value}'
DATABASE_URL="${this.dbUrl}"
APP_DEBUG='${this.configGenerator.APP_DEBUG.value}'`;

    this.step = 4;
  }

  startInstall() {
    this.step = 4.5;
    this.http.post('/install/', { config: this.generatedConfig, superuser: this.superuser }).subscribe(
        {
          next: (res: any) => {
            this.step = 5;
          },
          error: (err: any) => {
            this.step = 1;
            alert("An error occurred while installing Rosterboard. We'll take you back to the start so you can try again.");
          }
        }
    )
  }
}
