import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment'
import { CookieService } from 'ngx-cookie';

@Injectable({
  providedIn: 'root'
})

export class UploadFileService {
  public env = environment;
  public apiUrl = this.env['apiUrlScript']
  public uploadedFile: FormData = new FormData();
  private httpOptions: any;

  constructor(private http: HttpClient, private _cookieService: CookieService) {
    // inserting CSRF token in the http headers
    let csrf = this._cookieService.get("csrftoken");
    if (typeof (csrf) === 'undefined') {
      csrf = '';
    }
    this.httpOptions = {
      headers: new HttpHeaders({  
        'X-CSRFToken': csrf 
      })
    };
  }

  // API service for uploading the file
  public postFile(tid, lid, vid, file) {
    this.uploadedFile.append('docs', file, file.name);
    this.uploadedFile.append('type', 'file');
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/${vid}/`;

    return this.http.post(
      _url,
      this.uploadedFile,
      this.httpOptions,
    )
  }

}
