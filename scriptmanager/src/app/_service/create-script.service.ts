import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment'

@Injectable({
  providedIn: 'root'
})
export class CreateScriptService {
  public env =  environment;
  public apiUrl = this.env['apiUrlScript']

  public getScript(tid, lid){
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/`
    return this.httpClient.get(_url);
  }

  public postScript(tid, lid, data) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/`
    var ls = this.httpClient.post(
      _url,
      data
    );
    return ls;
  }

  public patchScript(tid, lid, data) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/`
    var ls = this.httpClient.patch(
      _url,
      data
    );
    return ls;
  }

  public deleteScript(tid, lid, srcipt_pk) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/${srcipt_pk}/`
    var ls = this.httpClient.delete(
      _url
    );
    return ls;
  }

  constructor(private httpClient: HttpClient) { }
}
