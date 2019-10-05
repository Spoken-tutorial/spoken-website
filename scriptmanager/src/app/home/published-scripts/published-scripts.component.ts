import { Component, OnInit } from '@angular/core';
import { CreateScriptService } from 'src/app/_service/create-script.service';

@Component({
  selector: 'app-published-scripts',
  templateUrl: './published-scripts.component.html',
  styleUrls: ['./published-scripts.component.sass']
})
export class PublishedScriptsComponent implements OnInit {
  public scripts: any = [];

  constructor(
    private scriptService: CreateScriptService
  ) { }

  ngOnInit() {
    this.scriptService.getPublishedScripts()
      .subscribe(
        (res) => {
          this.scripts = res['data'];
          console.log(this.scripts);
          console.log(Object.keys(this.scripts));
        },
        console.error
      )
  }

}
